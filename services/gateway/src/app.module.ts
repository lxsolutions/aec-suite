import { Module } from "@nestjs/common";
import { HealthController } from "./health/health.controller";
import { OrchestratorController } from "./orchestrator/orchestrator.controller";
import { RoverController } from "./rover/rover.controller";
import { ErpController } from "./erp/erp.controller";
import { EstateJointController } from "./estate-joint/estate-joint.controller";

@Module({
  imports: [],
  controllers: [
    HealthController,
    OrchestratorController,
    RoverController,
    ErpController,
    EstateJointController,
  ],
})
export class AppModule {}
