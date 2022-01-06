#!/usr/bin/env python3
import aws_cdk as cdk

from notify_delivery_schedule_app.notify_delivery_schedule_app_stack import NotifyDeliveryScheduleAppStack


app = cdk.App()
NotifyDeliveryScheduleAppStack(
    app, 
    "NotifyDeliveryScheduleAppStack",
    stack_name="NotifyDeliveryScheduleAppStack",
    description="Application that notifies delivery schedule."
)

app.synth()
