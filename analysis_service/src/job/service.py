import json
import time

import jsbeautifier
from langchain.schema import HumanMessage, SystemMessage
from src.job.config import job_config
from src.job.prompts import fn_job_analysis, system_prompt_job
from src.utils import LOGGER
from src.integrations.llm import extract_data_from_llm



def analyse_job(job_data):
    start = time.time()
    LOGGER.info("Start analyse job")

    output_analysis = extract_data_from_llm(job_data.job_description, system_prompt_job, fn_job_analysis)
    json_output = output_analysis

    LOGGER.info("Done analyse job")
    LOGGER.info(f"Time analyse job: {time.time() - start}")

    return json_output
