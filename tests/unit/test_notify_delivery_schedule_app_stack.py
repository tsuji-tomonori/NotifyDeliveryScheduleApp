import aws_cdk as core
import aws_cdk.assertions as assertions

from notify_delivery_schedule_app.notify_delivery_schedule_app_stack import NotifyDeliveryScheduleAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in notify_delivery_schedule_app/notify_delivery_schedule_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = NotifyDeliveryScheduleAppStack(app, "notify-delivery-schedule-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
