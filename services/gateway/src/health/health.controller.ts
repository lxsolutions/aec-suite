import { Controller, Get } from "@nestjs/common";

@Controller("health")
export class HealthController {
  @Get()
  health() {
    return { status: "ok", timestamp: new Date().toISOString() };
  }

  @Get("ready")
  ready() {
    return { status: "ready", timestamp: new Date().toISOString() };
  }

  @Get("live")
  liveness() {
    return { status: "live", timestamp: new Date().toISOString() };
  }
}
