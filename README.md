
1. Requirements
安装ffmpeg，miktex，找一下别人的博客

cd src/
pip install -r requirements.txt



2. Configure LLM API Keys
* **LLM API**:
  * Required for Planner & Coder.
  * Best Manim code quality achieved with **Claude-4-Opus**.
* **VLM API**:
  * Required for Planner Critic.
  * For layout and aesthetics optimization, provide **Gemini API key**.
  * Best quality achieved with **gemini-2.5-pro-preview-05-06**.
 
**Visual Assets API**:

* To enrich videos with icons, set `ICONFINDER_API_KEY` from [IconFinder](https://www.iconfinder.com/account/applications).




Generates a video from a single **knowledge point** specified in the script.

```bash
sh run_agent_single.sh --knowledge_point "Linear transformations and matrices"
```




