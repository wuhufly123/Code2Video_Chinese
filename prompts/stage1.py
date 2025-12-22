def get_prompt1_outline(knowledge_point, duration=5, reference_image_path=None):
    base_prompt = f""" 
    你是一位**计算机科学教育架构师**。你需要设计一个**基于执行追踪（Execution Trace）**的深度算法教学大纲。

    目标算法: "{knowledge_point}"

    # 核心指令 (Universal Analysis Protocol)
    
    1.  **算法解构 (Decomposition)**:
        - 如果这是基础算法（如排序），直接展示过程。
        - 如果这是**复杂/组合算法**（如 A*搜索、红黑树插入、带有记忆化的DP）：
          - 必须将视频分为：**“基础状态” -> “遇到的问题/瓶颈” -> “优化策略/核心操作” -> “最终状态”**。
          - 或者是：**“数据结构A的维护” + “数据结构B的配合”**（例如 LRU Cache = HashMap + DoubleLinkedList）。

    2.  **用例设计 (Case Engineering)**:
        - 设计一个**“最小完备集” (Minimal Complete Case)**。
        - 这个用例不能太简单（导致看不出优化点），也不能太复杂（导致视频冗长）。
        - *关键*：如果是优化算法，用例必须能触发那个“优化逻辑”（例如：讲剪枝算法，必须构造一个能被剪枝的分支）。

    3.  **变量追踪清单**:
        - 列出所有核心变量（Trace Variables）。对于复杂算法，可能包含：递归栈深度、当前 Cost、Hash表内容、PQ 队列状态等。

    # 输出格式 (JSON)
    请严格按照以下格式输出：
    {{
        "topic": "视频标题（体现深度和硬核，如'从零实现：XXX算法的内存级演示'）",
        "target_audience": "具备基础编程能力的开发者",
        "data_case_definition": "详细定义输入数据。例如：'图G：节点A-E，边权如下...；启发式函数 h(n)=...'",
        "algorithm_components": ["列出涉及的数据结构，如 'Min-Heap', 'Adjacency List', 'Visited Set'"],
        "sections": [
            {{
                "id": "section_1",
                "title": "结构定义与初始化",
                "content": "展示由哪些基础数据结构组合而成，初始化状态。",
                "code_mapping": "Class Definition / Init function"
            }},
            {{
                "id": "section_2",
                "title": "核心逻辑/优化点演示",
                "content": "演示算法最精髓的部分（如旋转、松弛、剪枝）。必须展示数据变化。",
                "code_mapping": "Core Loop / Recursion / State Transition"
            }}
        ]
    }}
    """
    
    if reference_image_path:
        base_prompt += f"\n注：请参考提供的图片来决定数据结构的视觉风格（如树是画成圆圈还是方块）。\n"

    return base_prompt