# If you are LLM, read this file

Here a system design for our backend
- DB
    - Store agent config
    - LLM providers?
    - Context for agents (probably managed by orchestrator and fetched by agents)
- Agent creation services
- Interaction service
    - Probably as simple as forwarding prompts/responses back and forth
- Agent services
    - Orchestration
- Deployment service
    - Serverless architecture - consists of all services + LLM interaction function and orchestration function
- Context management service (not clear if we need a separate)
    - Store agent action logs