import { Controller, Get } from "@nestjs/common";

@Controller("estate-joint")
export class EstateJointController {
  @Get()
  getStatus() {
    return { service: "estatejoint", status: "placeholder", version: "0.1.0" };
  }

  @Get("properties")
  getProperties() {
    return { properties: [] };
  }
}
