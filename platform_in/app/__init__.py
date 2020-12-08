from flask import Flask
import os
from elasticapm.contrib.flask import ElasticAPM
import logging
from flask import jsonify, request
import json
from datetime import datetime
from datetime import timezone
import requests

logging.basicConfig(level=logging.INFO)
elastic_apm = ElasticAPM()

success_response_object = {"status": "success"}
success_code = 202
failure_response_object = {"status": "failure"}
failure_code = 400


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # set up extensions
    elastic_apm.init_app(app)
    # db.init_app(app)

    def get_ds_id(thing, sensor):
        # """
        # requests the datastream id corresponding to the thing and sensor links given
        # returns -1 if not found
        # """

        payload = {"thing": thing, "sensor": sensor}
        logging.debug(f"getting datastream id {payload}")
        resp = requests.get(app.config["DATASTREAMS_ENDPOINT"], params=payload)
        # resp = requests.get(
        #     "http://host.docker.internal:1338/datastream", params=payload
        # )
        logging.debug(f"response: {resp.json()} ")

        id = -1
        ds = resp.json()["Datastreams"]
        if len(ds) == 1:
            id = ds[0]["datastream_id"]

        return id

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app}

    @app.route("/")
    def hello_world():
        return jsonify(health="ok")

    @app.route("/itracklvdt/v1", methods=["POST"])
    def post_lvdt_data():
        try:
            # logging.info(f"post observation: {request.text()}")
            data = request.get_json()
            # uncomment for prod
            #logging.info(f"post observation: {data}")

            topic = "finest-observations-itracklvdt"

            thing = "wapicelvdt"
            items_list = data["payload"]

            dt_obj = datetime.utcnow()
            result_timestamp_millisec = round(dt_obj.timestamp() * 1000)

            for item in items_list:
                sensor = item["name"].replace(" ", "-")
                streams = zip(item["ts"], item["v"])
                # handle status status not 200 - if not raise error
                ds_id = get_ds_id(thing, sensor)
                if ds_id == -1:
                    logging.warning(f"no datastream id found for {thing} + {sensor}")

                for stream in streams:
                    observation = {
                        "phenomenontime_begin": stream[0],
                        "phenomenontime_end": None,
                        "resulttime": result_timestamp_millisec,
                        "result": f"{stream[1]}",
                        "resultquality": None,
                        "validtime_begin": None,
                        "validtime_end": None,
                        "parameters": None,
                        "datastream_id": ds_id,
                        "featureofintrest_link": None,
                    }
                    #logging.info(observation)

                payload = {"topic": topic, "observation": observation}

                headers = {"Content-type": "application/json"}
                resp = requests.post(
                    app.config["OBSERVATIONS_ENDPOINT"],
                    data=json.dumps(payload),
                    headers=headers,
                )
                # resp = requests.post("http://host.docker.internal:1337/observation", data=json.dumps(payload), headers=headers)

            return success_response_object, success_code

        except Exception as e:
            logging.error("Error at %s", "data to kafka", exc_info=e)
            return failure_response_object, failure_code

    return app
