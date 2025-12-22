import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from threading import Lock

from gpt_request import request_gemini_with_video
from prompts import get_prompt_aes
from utils import extract_answer_from_response, eva_video_list


@dataclass
class EvaluationResult:
    element_layout: float
    attractiveness: float
    logic_flow: float
    accuracy_depth: float
    visual_consistency: float
    overall_score: float
    detailed_feedback: str
    knowledge_point: str = ""


class VideoEvaluator:
    def __init__(self, request_gemini_function):
        """
        Initialize the video evaluator
        """
        self.request_gemini_with_video = request_gemini_function
        self._progress_lock = Lock()

    def evaluate_video(self, video_path: str, knowledge_point: str, log_id: str = None) -> EvaluationResult:
        """
        Evaluate a single teaching video

        Args:
            video_path: Video file path
            knowledge_point: Knowledge point description (required for targeted evaluation)
            log_id: Log ID

        Returns:
            EvaluationResult: Object containing detailed evaluation results
        """
        evaluation_prompt = get_prompt_aes(knowledge_point)

        try:
            response = self.request_gemini_with_video(
                prompt=evaluation_prompt, video_path=video_path, log_id=log_id, max_tokens=10000, max_retries=3
            )
            result = self._parse_evaluation_response(response)
            result.knowledge_point = knowledge_point
            return result

        except Exception as e:
            print(f"视频评估期间出错: {str(e)}")
            return self._create_error_result(str(e))

    def evaluate_video_batch(
        self, video_list: List[Dict[str, Any]], log_id: str = None, max_workers: int = 3, use_parallel: bool = True
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple teaching videos in batch (supports parallel processing)

        Args:
            video_list: List[Dict[str, Any]], each element contains {'path': str, 'knowledge_point': str}
            log_id: Log ID
            max_workers: Maximum number of parallel worker threads (suggest 2-5 to avoid API call frequency issues)
            use_parallel: Whether to use parallel processing, default True

        Returns:
            List[EvaluationResult]: List of evaluation results (in the same order as input)
        """
        if not use_parallel or len(video_list) == 1:
            return self._evaluate_video_batch_sequential(video_list, log_id)

        return self._evaluate_video_batch_parallel(video_list, log_id, max_workers)

    def _evaluate_video_batch_sequential(self, video_list: List[Dict[str, Any]], log_id: str = None) -> List[EvaluationResult]:
        results = []

        for i, video_info in enumerate(video_list):
            video_path = video_info.get("path", "")
            knowledge_point = video_info.get("knowledge_point", "")

            if not knowledge_point:
                print(f"警告: 视频 {i+1} 缺少知识点信息，可能会影响评估准确性")

            print(f"正在评估视频 {i+1}/{len(video_list)}: {video_path}")
            print(f"知识点: {knowledge_point}")

            result = self.evaluate_video(
                video_path=video_path, knowledge_point=knowledge_point, log_id=f"{log_id}_video_{i+1}" if log_id else None
            )

            results.append(result)
        return results

    def _evaluate_video_batch_parallel(
        self, video_list: List[Dict[str, Any]], log_id: str = None, max_workers: int = 3
    ) -> List[EvaluationResult]:
        """Parallel processing mode"""
        print(f"开始并行评估 {len(video_list)} 个视频，使用 {max_workers} 个工作线程...")

        results = [None] * len(video_list)
        completed_count = 0
        start_time = time.time()

        def evaluate_single_video(index: int, video_info: Dict[str, Any]) -> tuple:
            """Wrapper function to evaluate a single video"""
            video_path = video_info.get("path", "")
            knowledge_point = video_info.get("knowledge_point", "")

            if not knowledge_point:
                with self._progress_lock:
                    print(f"警告: 视频 {index+1} 缺少知识点信息，可能会影响评估准确性")

            try:
                result = self.evaluate_video(
                    video_path=video_path, knowledge_point=knowledge_point, log_id=f"{log_id}_video_{index+1}" if log_id else None
                )
                return index, result, None
            except Exception as e:
                error_result = self._create_error_result(f"并行评估错误: {str(e)}")
                return index, error_result, str(e)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(evaluate_single_video, i, video_info): i for i, video_info in enumerate(video_list)
            }
            for future in as_completed(future_to_index):
                try:
                    index, result, error = future.result()
                    results[index] = result

                    with self._progress_lock:
                        completed_count += 1
                        elapsed_time = time.time() - start_time
                        avg_time_per_video = elapsed_time / completed_count
                        eta = avg_time_per_video * (len(video_list) - completed_count)

                        print(f"已完成 {completed_count}/{len(video_list)} " f"(耗时: {elapsed_time:.1f}s, ETA: {eta:.1f}s)")

                        if error:
                            print(f"警告: 视频 {index+1} 评估出错: {error}")
                        else:
                            video_path = video_list[index].get("path", "")
                            knowledge_point = video_list[index].get("knowledge_point", "")
                            print(
                                f"✓ 视频 {index+1}: {video_path} (知识点: {knowledge_point}) "
                                f"- 得分: {result.overall_score:.1f}/100"
                            )

                except Exception as e:
                    with self._progress_lock:
                        print(f"警告: 处理视频 {index+1} 的结果时出错: {str(e)}")

        total_time = time.time() - start_time
        print(f"\n并行评估完成！总耗时: {total_time:.1f}s, 平均每视频: {total_time/len(video_list):.1f}s")

        return results

    def _parse_evaluation_response(self, response: str) -> EvaluationResult:
        """Parse the evaluation response from MLLM"""
        try:
            response = extract_answer_from_response(response=response)
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                # multi-dimension
                element_layout = float(data.get("element_layout", {}).get("score", 0))
                attractiveness = float(data.get("attractiveness", {}).get("score", 0))
                logic_flow = float(data.get("logic_flow", {}).get("score", 0))
                accuracy_depth = float(data.get("accuracy_depth", {}).get("score", 0))
                visual_consistency = float(data.get("visual_consistency", {}).get("score", 0))

                # TODO: overall
                overall_score = element_layout + attractiveness + logic_flow + accuracy_depth + visual_consistency

                # detailed feedback
                detailed_feedback = self._build_detailed_feedback(data)

                return EvaluationResult(
                    element_layout=element_layout,
                    attractiveness=attractiveness,
                    logic_flow=logic_flow,
                    accuracy_depth=accuracy_depth,
                    visual_consistency=visual_consistency,
                    overall_score=round(overall_score, 2),
                    detailed_feedback=detailed_feedback,
                )
            else:
                return self._extract_scores_from_text(response)

        except Exception as e:
            print(f"Error parsing evaluation response: {str(e)}")
            return self._create_error_result(str(e))

    def _extract_scores_from_text(self, response: str) -> EvaluationResult:
        """Extract scores from text response (fallback method)"""
        # Use regex to extract scores
        patterns = {
            "element_layout": r"Element Layout.*?(\d+(?:\.\d+)?)",
            "attractiveness": r"Attractiveness.*?(\d+(?:\.\d+)?)",
            "logic_flow": r"Logic Flow.*?(\d+(?:\.\d+)?)",
            "accuracy_depth": r"Accuracy.*?Depth.*?(\d+(?:\.\d+)?)",
            "visual_consistency": r"Visual Consistency.*?(\d+(?:\.\d+)?)",
        }

        scores = {}
        for dimension, pattern in patterns.items():
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                scores[dimension] = float(match.group(1))
            else:
                scores[dimension] = 0.0

        overall_score = (
            scores["element_layout"] * 0.2
            + scores["attractiveness"] * 0.2
            + scores["logic_flow"] * 0.2
            + scores["accuracy_depth"] * 0.2
            + scores["visual_consistency"] * 0.2
        )

        return EvaluationResult(
            element_layout=scores["element_layout"],
            attractiveness=scores["attractiveness"],
            logic_flow=scores["logic_flow"],
            accuracy_depth=scores["accuracy_depth"],
            visual_consistency=scores["visual_consistency"],
            overall_score=round(overall_score, 2),
            detailed_feedback=response,
        )

    def _build_detailed_feedback(self, data: Dict) -> str:
        feedback_sections = []
        dimensions = [
            ("元素布局 (Element Layout)", "element_layout"),
            ("吸引力 (Attractiveness)", "attractiveness"),
            ("逻辑流 (Logic Flow)", "logic_flow"),
            ("准确度与深度 (Accuracy & Depth)", "accuracy_depth"),
            ("视觉一致性 (Visual Consistency)", "visual_consistency"),
        ]

        for name, key in dimensions:
            section_data = data.get(key, {})
            score = section_data.get("score", 0)
            feedback = section_data.get("feedback", "未提供反馈")
            feedback_sections.append(f"**{name} ({score} 分):**\n{feedback}")
        summary = data.get("summary", "")
        strengths = data.get("strengths", [])
        improvements = data.get("improvements", [])

        detailed_feedback = "\n\n".join(feedback_sections)

        if summary:
            detailed_feedback += f"\n\n**总体总结 (Overall Summary):**\n{summary}"

        if strengths:
            detailed_feedback += f"\n\n**主要优点 (Key Strengths):**\n" + "\n".join([f"• {s}" for s in strengths])

        if improvements:
            detailed_feedback += f"\n\n**改进建议 (Areas for Improvement):**\n" + "\n".join([f"• {i}" for i in improvements])

        return detailed_feedback

    def _create_error_result(self, error_message: str) -> EvaluationResult:
        return EvaluationResult(
            element_layout=0.0,
            attractiveness=0.0,
            logic_flow=0.0,
            accuracy_depth=0.0,
            visual_consistency=0.0,
            overall_score=0.0,
            detailed_feedback=f"评估期间出错: {error_message}",
        )

    def generate_evaluation_report(self, results: List[EvaluationResult], output_path: str = None) -> str:
        if not results:
            return "由于评估过程出错，无法生成报告。"

        total_videos = len(results)
        avg_scores = {
            "element_layout": sum(r.element_layout for r in results) / total_videos,
            "attractiveness": sum(r.attractiveness for r in results) / total_videos,
            "logic_flow": sum(r.logic_flow for r in results) / total_videos,
            "accuracy_depth": sum(r.accuracy_depth for r in results) / total_videos,
            "visual_consistency": sum(r.visual_consistency for r in results) / total_videos,
            "overall": sum(r.overall_score for r in results) / total_videos,
        }
        report = f"""# 视频教学质量评估报告

## 视频评估详情

"""

        for i, result in enumerate(results, 1):
            report += f"""### 视频 {i}
- **教学主题**: {result.knowledge_point}
- **综合得分**: {result.overall_score}/100
- 元素布局: {result.element_layout/20*100:.1f}
- 吸引力: {result.attractiveness/20*100:.1f}
- 逻辑流: {result.logic_flow/20*100:.1f}
- 准确度与深度: {result.accuracy_depth/20*100:.1f}
- 视觉一致性: {result.visual_consistency/20*100:.1f}

**详细反馈**:
{result.detailed_feedback}
---

"""
        report += f"""## 总体统计
- **已评估视频总数**: {total_videos}
- **平均综合得分**: {avg_scores['overall']:.2f}/100

## 各维度平均表现 (百分制)
- 元素布局: {avg_scores['element_layout']/20*100:.2f}
- 吸引力: {avg_scores['attractiveness']/20*100:.2f}
- 逻辑流: {avg_scores['logic_flow']/20*100:.2f}
- 准确度与深度: {avg_scores['accuracy_depth']/20*100:.2f}
- 视觉一致性: {avg_scores['visual_consistency']/20*100:.2f}

"""

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"评估报告已保存至: {output_path}")

        return report


def evaluate_main():
    json_file = "XXX/json_files/long_video_topics_list.json"
    with open(json_file, "r", encoding="utf-8") as f:
        knowledge_points = json.load(f)

    evaluator = VideoEvaluator(request_gemini_with_video)

    # ----------------------------------------------------------------------------------------
    # TODO: target folder
    video_list = eva_video_list(
        knowledge_points=knowledge_points,
        base_dir="XXX/CASES/Sep_ACL_Gemini",
    )

    batch_results = evaluator.evaluate_video_batch(video_list, max_workers=3, use_parallel=True)

    report = evaluator.generate_evaluation_report(batch_results, output_path=None)
    print(report)


if __name__ == "__main__":
    evaluate_main()