# prompts/stage4.py

def get_prompt4_layout_feedback(section, position_table):
    return f"""
1. 分析要求 (ANALYSIS REQUIREMENTS):
- 请仅从**布局(Layout)**和**空间位置(Spatial Positioning)**的角度分析这个 Manim 教育视频。
- 参考提供的网格图进行精确的空间分析。
- 核心目标：消除遮挡、重叠，并优化网格空间的利用率。

2. 内容上下文 (Content Context):
- 标题: {section.title}
- 讲解词: {'; '.join(section.lecture_lines)}
- 当前网格占用情况: {position_table}

3. 视觉锚点系统 (6*6 grid, 仅右侧区域):
lecture | A1 A2 A3 A4 A5 A6 | B1 B2 B3 B4 B5 B6 | C1 C2 C3 C4 C5 C6 | D1 D2 D3 D4 D5 D6 | E1 E2 E3 E4 E5 E6 | F1 F2 F3 F4 F5 F6

- 点定位 (point): self.place_at_grid(obj, 'B2', scale_factor=0.8)
- 区域定位 (area): self.place_in_area(obj, 'A1', 'C3', scale_factor=0.7)

4. 布局评估 (检查所有项):
- **遮挡 (Obstruction)**: 动画元素是否遮挡了左侧的讲解文字？[严重]
- **重叠 (Overlap)**: 动画元素之间（公式、标签、图形）是否发生重叠？
- **出界 (Off-screen)**: 元素是否被切掉或超出了屏幕可视范围？[特别是长文本标签]
- **网格违规**: 空间利用是否不合理（太挤或太散）？
- **未消失**: 检查是否有应该淡出但未淡出的元素。

5. 强制约束:
- 颜色: 指出颜色不清晰的地方。
- 字体/比例: 针对网格位置调整字体大小和素材缩放。
- 一致性: **不要**对左侧讲解词做任何位置或大小动画，只改变颜色。
- 邻近性: 确保标签文字与其对应的物体在 1 个网格单位以内。

6. 重要：必须严格按照以下 JSON 结构输出:
{{
    "layout": {{
        "has_issues": true,  // 如果有明显布局问题则为 true
        "improvements": [
            {{
                "problem": "具体问题描述 (中文)",
                "solution": "建议修改的代码逻辑，例如：将圆形从 C3 移到 E3",
                "line_number": X, // 估算代码行号
                "object_affected": "受影响的对象名"
            }},
            ...
        ]
    }}
}}

7. 解决方案要求:
- 在解决方案中提供具体的网格坐标建议。
- 仅列出最影响视觉体验的 3 个布局问题！
- 不要给出视频时间戳。
- 问题描述要简洁，解决方案要具体可执行。
"""


def get_feedback_list_prefix(feedback_improvements):
    """
    生成反馈列表的前缀说明
    """
    return f"""       
MLLM 视觉反馈建议：基于对生成视频的分析，请解决以下布局问题：
{chr(10).join([f"- {improvement}" for improvement in feedback_improvements])}
"""


def get_feedback_improve_code(feedback, code):
    return f"""
你是一位 Manim v0.19.0 教育动画专家。

**必须遵守 (MANDATORY)**:
- 基于以下反馈，修改当前的 Manim 代码。
- 动画和标签请使用明亮、高对比度的颜色！
- **严禁**对左侧讲解词（lecture lines）应用任何位置或大小动画，只允许改变颜色（highlight）。
- 仅输出更新后的完整 Python 代码。不需要任何解释。

反馈意见 (Feedback):
{feedback}

---

当前代码 (Current Code):
```python
{code}
"""