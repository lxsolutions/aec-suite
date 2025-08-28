import { Controller, Get } from "@nestjs/common";

@Controller("rover")
export class RoverController {
  @Get()
  getStatus() {
    return { service: "rover", status: "placeholder", version: "0.1.0" };
  }

  @Get("operations")
  getOperations() {
    return { operations: [] };
  }
}
