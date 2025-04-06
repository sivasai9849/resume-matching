import time

from src.matching.prompts import fn_matching_analysis, system_prompt_matching
from src.utils import LOGGER
from src.integrations.llm import extract_data_from_llm



def generate_content(job, candidate):
    content = "\nRequirement:" + str(job) + "\nCandidate:" + str(candidate)
    return content


def analyse_matching(matching_data):
    start = time.time()
    LOGGER.info("Start analyse matching")

    content = generate_content(job=matching_data.job, candidate=matching_data.candidate)

    output_analysis = extract_data_from_llm(content, system_prompt_matching, fn_matching_analysis)

    json_output = output_analysis

    # Extract scores and store them in a list
    weights = {
        "degree": 0.1,  # The importance of the candidate's degree
        "experience": 0.2,  # The weight given to the candidate's relevant work experience
        "technical_skill": 0.3,  # Weight for technical skills and qualifications
        "responsibility": 0.25,  # How well the candidate's past responsibilities align with the job
        "certificate": 0.1,  # The significance of relevant certifications
        "soft_skill": 0.05,  # Importance of soft skills like communication, teamwork, etc.
    }
    total_weight = 0
    weighted_score = 0

    for section in json_output:
        if section != "summary_comment":
            weighted_score += int(json_output[section]["score"]) * weights[section]
            total_weight += weights[section]

    final_score = weighted_score / total_weight

    json_output["score"] = final_score

    LOGGER.info("Done analyse matching")
    LOGGER.info(f"Time analyse matching: {time.time() - start}")

    return json_output
