import os

def get_prompt3_code(regenerate_note, section, base_class):
    return f"""
    你是一位精通 Manim 的 Python 专家。请编写代码生成一个**解释复杂算法执行逻辑**的视频片段。

    {regenerate_note}

    ### 核心任务：通用算法可视化 (Universal Algorithm Visualization)
    
    不要硬编码特定的形状，而是根据算法逻辑选择最合适的 Manim 对象。

    ### 1. 动态布局系统 (Dynamic Layout System)
    ```python
    # 推荐的标准初始化
    code_obj = Code(code=..., language="python").to_edge(LEFT).scale(0.8)
    
    # 右侧主容器，所有视觉元素放入这里，方便整体缩放/移动
    main_group = VGroup().to_edge(RIGHT)
    
    # 如果是复杂算法，内部再分组
    # e.g., graph_group = VGroup(...).next_to(main_group, UP)
    #       aux_struct_group = VGroup(...).next_to(main_group, DOWN)
    ```

    ### 2. 交互与逻辑表现 (Interaction & Logic)
    - **代码高亮**: `self.play(Indicate(code_obj.code[line_idx]))`
    - **逻辑外显化**: 
      - 不要只让数据变色。如果代码里有 `if a > b`，你必须在屏幕上写出 `MathTex("5 > 3")`，显示它成立（变绿）或不成立（变红），然后再执行后续动作。
      - **递归**: 如果涉及递归，请在屏幕一角维护一个 `VGroup` 代表 Stack，每层递归 `add` 一个矩形，返回时 `remove`。

    ### 3. 数据结构映射库 (Mapping Library)
    - **Array/DP Table**: 使用 `VGroup` of `Square` 或 `Table` 类。必须标 `Index`。
    - **Tree/Graph**: 优先使用 `Graph` 类（如果节点关系固定），或者手动通过 `Circle` 和 `Line` 构建，以便灵活移动节点。
    - **Pointer/Reference**: `Arrow` 是必须的。不要只改变颜色，要用箭头指向当前操作的对象。

    ### 任务输入
    - 标题: {section.title}
    - 脚本: {section.lecture_lines}
    - 动画指令: {section.animations}

    ### 代码规范
    - 必须继承 `TeachingScene`。
    - 确保代码逻辑完整：变量先定义后使用。
    - 节奏：`self.wait(1)` 非常重要，给观众思考时间。

    ### 参考代码结构
    ```python
    from manim import *
    {base_class}

    class {section.id.title().replace('_', '')}Scene(TeachingScene):
        def construct(self):
            # 1. Setup Layout
            code_raw = \"\"\"def complex_algo(data):
    if check(data):
        optimize(data)
    else:
        process(data)\"\"\"
            code = Code(code=code_raw, ...).to_edge(LEFT)
            self.play(Create(code))
            
            # 2. Setup Data Structures (Example: A composite structure)
            # Main Data (e.g., Array)
            array_group = VGroup(*[Square() for _ in range(5)]).arrange(RIGHT).to_edge(UP)
            # Aux Data (e.g., Stack)
            stack_group = VGroup().to_edge(DOWN)
            
            # 3. Execution Trace
            # Step 1: Check
            self.play(Indicate(code.code[1]))
            check_label = MathTex("Check: Is Valid?").next_to(array_group, DOWN)
            self.play(Write(check_label))
            
            # Step 2: Visual Feedback
            self.play(array_group[0].animate.set_color(GREEN)) # Valid
            self.play(FadeOut(check_label))
            
            # Step 3: Optimization phase
            self.play(Indicate(code.code[2]))
            # Show optimization effect (e.g., merge nodes)
            self.play(ReplacementTransform(array_group[0], array_group[1]))
            
            self.wait(2)
    ```

6. **强制约束**:
- 颜色使用明亮的 hex 颜色。
- 严禁使用复杂的 3D 场景（除非必要），保持 2D 清晰图解。
- 不要在动画中改变左侧 lecture_lines 的位置或大小，只改变颜色。
"""

def get_regenerate_note (attempt, MAX_REGENERATE_TRIES):
    return f"""注意：这是第 {attempt}/{MAX_REGENERATE_TRIES} 次尝试生成代码。上一次生成的代码运行失败或效果不佳。请：
简化复杂的动画逻辑，优先保证运行成功。
确保所有的变量在使用前都已定义。
检查 self.wait () 是否充足。
"""