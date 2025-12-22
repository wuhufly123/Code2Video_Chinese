import json

def get_prompt2_storyboard(outline, reference_image_path):
    base_prompt = f""" 
    你是一位**硬核算法可视化导演**。请将大纲转化为详细的 Manim 动画脚本。

    # 通用视觉映射系统 (Universal Visual Mapping System)

    1.  **多维布局策略 (Layout Strategy)**:
        - **Code Window (左侧 40%)**: 始终显示代码，高亮执行行。
        - **Main Visual Area (右侧 60%)**: 
          - 如果算法涉及单一结构（如数组）：居中显示。
          - 如果算法涉及**组合结构**（如 图算法 + 优先队列）：
            - **上部**: 主结构（Graph/Tree）。
            - **下部**: 辅助结构（Queue/Stack/Table）。
        - **State Monitor (底部/角落)**: 实时显示的变量值（Cost, Index, True/False）。

    2.  **抽象概念实体化**:
        - **引用/指针**: 必须画成箭头 (Arrow)。
        - **递归**: 必须画成**调用栈 (Call Stack)**，用一个个压入的矩形块表示，旁边标注参数值。
        - **比较/判断**: 必须在屏幕上显示临时的数学不等式（例如 `dist[B] > new_dist`），判定后再消失。
        - **记忆化/缓存**: 画成一个表格 (Table/Grid)，命中时高亮闪烁。

    3.  **脚本要求**:
        - 每一句旁白（Lecture Line）必须对应代码的解释。
        - 每一个动画（Animation）必须对应数据的变化（Create, Transform, FadeOut）。

    ## 输入大纲
    {outline}
    """

    base_prompt += """
    请输出以下 JSON 格式：
    {
        "sections": [
            {
                "id": "section_id",
                "title": "标题",
                "lecture_lines": ["..."],
                "animations": [
                    "Define Visual Layout: Split Right Area into Top (Graph) and Bottom (Priority Queue).",
                    "Action: Highlight code line `heapq.heappush(pq, (0, start))`.",
                    "Visual: Create a Circle labeled 'Start' in Graph. Create a small Square labeled '(0, S)' appearing in the Queue area.",
                    "Monitor: Update text `Current Cost = 0`."
                ]
            }
        ]
    }
    """
    return base_prompt


def get_prompt_download_assets(storyboard_data):
    return f"""
分析这份教育视频分镜脚本，识别出最多 4 个**必须**使用下载图标/图片（而非手动绘制形状）来表示的关键视觉元素。

内容 (Content):
{storyboard_data}

选择标准 (Selection Criteria):
1. 仅选择出现在**介绍 (Introduction)** 或 **应用 (Application)** 章节中的元素，且必须满足：
   - 现实世界中可识别的物理对象
   - 视觉特征鲜明，仅用通用几何形状不足以表达
   - 具体的实物，而非抽象概念
2. 优先选择：具体的动物、角色、交通工具、工具、设备、地标、日常物品。
3. **忽略且绝不包含**：
   - 抽象概念（如：正义、交流）
   - 思想的符号或图标（如：字母、公式、图表、数据结构树）
   - 几何形状、箭头或数学相关的视觉元素
   - 任何完全由基本形状组成且无独特视觉身份的物体

输出格式 (Output format):
- **仅输出英文关键词**（为了适配搜索引擎），每个关键词占一行，全小写，无编号，无额外文本。
"""


def get_prompt_place_assets(asset_mapping, animations_structure):
    return f"""
你需要通过插入已下载的素材来增强动画描述。

可用素材列表 (Asset list):
{asset_mapping}

当前动画数据 (Current Animations Data):
{animations_structure}

指令 (Instructions):
- 对于每一个动画步骤，判断是否应该融入已下载的素材。
- 仅为需要的动画步骤选择最相关的一个素材。
- 以此格式插入素材的**抽象路径**：[Asset: XXX]。
- **仅限**在**第一个和最后一个**章节中使用素材。
- 保持结构不变：返回一个包含 section_index, section_id 和 enhanced animations 的 JSON 数组。
- 仅修改动画描述以包含素材引用。
- 不要修改 section_index 或 section_id。

仅返回增强后的动画数据，必须是有效的 JSON 数组格式：
"""
