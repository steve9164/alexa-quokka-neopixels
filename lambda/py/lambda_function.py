# -*- coding: utf-8 -*-

# This is a simple Hello World Alexa Skill, built using
# the decorators approach in skill builder.

import logging
import json
import binascii

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

import boto3

color_slot = "color"
# For now choose colours that encode nicely in utf-8
# Can encode with base64 but Quokka has a small 32 byte limit on message length
colormap = {
    "red": (127, 0, 0),
    "green": (0, 127, 0),
    "blue": (0, 0, 127),
    "white": (127, 127, 127),
    "black": (0, 0, 0),
}

thingName = 'ESP8266-Quokka-LED'

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MissingColor(ValueError):
    pass

def set_neopixel_color(color_str):
    if color_str not in colormap:
        raise MissingColor('Color not in colour map')
    colour_bytes = bytes(colormap[color_str])
    msg = binascii.b2a_base64(6*colour_bytes).decode('utf-8') # Only set 6 because of radio message restrictions
    shadow_update = {
        "state": {
            "desired": {
                "neopixels": msg
            }
        }
    }
    client = boto3.client("iot-data", region_name="ap-southeast-2")
    client.update_thing_shadow(thingName=thingName, payload=json.dumps(shadow_update))



@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response
    speech_text = "Welcome to set neopixel colour."
    set_neopixel_color('black')

    return handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).set_should_end_session(
        False).response


@sb.request_handler(can_handle_func=is_intent_name("SetNeopixelColorIntent"))
def hello_world_intent_handler(handler_input):
    """Handler for SetNeopixelColor Intent."""
    # type: (HandlerInput) -> Response
    slots = handler_input.request_envelope.request.intent.slots
    color_str = slots[color_slot].value
    try:
        set_neopixel_color(color_str)
        speech_text = f"Setting neopixel colour to {color_str}"
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text)).set_should_end_session(
            True).response
    except MissingColor:
        speech = "I'm sorry. I didn't recognise that colour. Try a different colour"
        reprompt = (
            "I'm sorry. I didn't recognise that colour. Try a different colour. "
            "You can set the colour of the neopixels by saying, make the neopixels blue"
        )
        return handler_input.response_builder.speak(speech).ask(reprompt).response
        


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Change the colour of the neopixels by saying, make the neopixels red"

    return handler_input.response_builder.speak(speech_text).ask(
        speech_text).set_card(SimpleCard(
            "Hello World", speech_text)).response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    return handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "The Hello World skill can't help you with that.  "
        "You can say hello!!")
    reprompt = "You can say hello!!"
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for Session End."""
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    # type: (HandlerInput, Exception) -> Response
    logger.error(exception, exc_info=True)

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


handler = sb.lambda_handler()