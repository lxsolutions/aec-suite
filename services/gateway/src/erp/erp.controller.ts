import { Controller, Get } from "@nestjs/common";

@Controller("erp")
export class ErpController {
  @Get()
  getStatus() {
    return { service: "erp-bridge", status: "placeholder", version: "0.1.0" };
  }

  @Get("connections")
  getConnections() {
    return { connections: [] };
  }
}
