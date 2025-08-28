import { Controller, Get } from "@nestjs/common";

@Controller("orchestrator")
export class OrchestratorController {
  @Get()
  getStatus() {
    return { service: "orchestrator", status: "placeholder", version: "0.1.0" };
  }

  @Get("workflows")
  getWorkflows() {
    return { workflows: [] };
  }
}
