# AI Agent Build
AI Agent Builder for Swiss AI Hackathon

# Install
My setup for this hackathon in case you need it (open for discussion)
```bash
$ brew install pyenv pyenv-virtualenv
# Then follow this to add to the environment https://github.com/pyenv/pyenv?tab=readme-ov-file#b-set-up-your-shell-environment-for-pyenv
$ pyenv install 3.13
$ pyenv virtualenv 3.13 swiss-ai-hackathon
$ pyenv activate swiss-ai-hackathon
```

# Backend

Create a `backend/src/.env` file and populate it with LLM provider keys:
```bash
OPENAI_KEY=<key>
SWISS_AI_PLATFORM_API_KEY=<key>
```
