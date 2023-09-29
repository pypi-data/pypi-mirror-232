import os
import openai
import time
import csv
import json
from typing import Optional, Dict, List
import pandas as pd

RETRY_SLEEP_SECONDS = 0.5

def format_prompt_completion(prompt, completion, start_sequence="\n\n###\n\n", end_sequence="END"):
    """
    Formats a prompt and its completion.

    Args:
        prompt (str): The prompt text.
        completion (str): The completion text.
        start_sequence (str, optional): The starting sequence. Defaults to "\n\n###\n\n".
        end_sequence (str, optional): The ending sequence. Defaults to "END".

    Returns:
        dict: A dictionary with formatted prompt and completion.
    """
    formatted_prompt = prompt.strip() + start_sequence
    formatted_completion = completion.strip() + end_sequence
    return {"prompt": formatted_prompt, "completion": formatted_completion}

def format_prompt_completion_df(prompt, completion, start_sequence="\n\n###\n\n", end_sequence="END"):
    """
    Formats a prompt and its completion into a DataFrame.

    Args:
        prompt (str): The prompt text.
        completion (str): The completion text.
        start_sequence (str, optional): The starting sequence. Defaults to "\n\n###\n\n".
        end_sequence (str, optional): The ending sequence. Defaults to "END".

    Returns:
        pandas.DataFrame: A DataFrame with formatted prompt and completion.
    """
    formatted_prompt = prompt.strip() + start_sequence
    formatted_completion = completion.strip() + end_sequence
    return pd.DataFrame({"formatted_prompt": [formatted_prompt], "formatted_completion": [formatted_completion]})

def df_to_json(df, json_output):
    """
    Converts a DataFrame to JSON and saves it to a file.

    Args:
        df (pandas.DataFrame): The DataFrame to convert and save.
        json_output (str): The path to the output JSON file.
    """
    mode = 'a' if os.path.exists(json_output) else 'w'
    try:
        with open(json_output, mode) as f:
            # Convert the DataFrame to a list of dictionaries (records)
            records = df.to_dict(orient='records')
            for response in records:
                f.write(json.dumps(response) + '\n')
    except Exception as e:
        print(f"Error while saving responses to JSON: {e}")
        print(df)

def list_to_csv(data_list, output_file):
    """
    Saves a list of dictionaries to a CSV file.

    Args:
        data_list (list of dict): The list of dictionaries to save.
        output_file (str): The path to the output CSV file.
    """
    if not data_list:
        print("Data list is empty. Nothing to save.")
        return
    
    mode = 'a' if os.path.exists(output_file) else 'w'
    
    with open(output_file, mode, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data_list[0].keys())
        
        if mode == 'w':
            writer.writeheader()
        
        writer.writerows(data_list)

def df_to_csv(df, output_file):
    """
    Appends a DataFrame to a CSV file. If the file does not exist, it creates
    it with the header.

    Args:
        output_file (str): The path to the output CSV file.
        df (pandas.DataFrame): The DataFrame to append.
    """
    if not os.path.isfile(output_file):
        df.to_csv(output_file, index=False)
    else:
        df.to_csv(output_file, mode='a', header=False, index=False)

def parse_json_formatted(json_string, output_file, context=None):
    """
    Parses a JSON-formatted string, processes the data, and saves it to a file.

    Args:
        json_string (str): The JSON-formatted string to parse.
        output_file (str): The path to the output JSON file.
        context (str, optional): Additional context information. Defaults to None.
    """
    try:
        # Load the JSON array into a list of dictionaries
        data_list = json.loads(json_string)

        # Transform the list of dictionaries into a pandas DataFrame
        df = pd.DataFrame(data_list)

        # Initialize a DataFrame to hold the newly formatted data
        formatted_data = pd.DataFrame(columns=['formatted_prompt', 'formatted_completion'])

        # Loop through each row in the DataFrame and format the prompts and completions
        for index, row in df.iterrows():
            prompt = row['prompt']
            completion = row['completion']
            formatted_data = pd.concat([formatted_data, format_prompt_completion_df(prompt, completion)], ignore_index=True)

        # Save the formatted data as JSON
        df_to_json(formatted_data, output_file)

    except json.decoder.JSONDecodeError as e:
        print("\n", e, "\n")
        print("Error parsing JSON. Skipping context ... \n\n", context)

def generate_user_prompt(num_questions: int, question_type: str) -> str:
    """
    Generates the initial user prompt based on the number and type of questions.

    Args:
        num_questions (int): The number of questions to generate.
        question_type (str): The type of questions (e.g., "open-ended", "yes/no", "multiple-choice", etc.).

    Returns:
        str: The generated initial user prompt.
    """

    # Define static questions for different question types
    static_questions = {
        "open-ended": ["What is the capital of France", "How does photosynthesis work", "Where is the Eiffel Tower located", "Why do birds migrate", "When did World War II end"],
        "yes/no": ["Is the sky blue", "Can you swim", "Do cats have tails", "Will it rain tomorrow", "Did you eat breakfast"],
        "multiple-choice": ["Which of the following fruits is red", "Select the option that is a prime number", "Pick the choice that represents a mammal", "Choose the correct answer to 2 + 2", "Which planet is closest to the Sun"],
        "closed-ended": ["On a scale of 1 to 5, how satisfied are you with our service", "Rate your agreement from 1 to 5 with the statement", "How likely are you to recommend our product from 1 to 5", "How would you rate your experience from 1 to 5", "Rate your knowledge level from 1 to 5"],
        "ranking": ["Please rank the following movies in order of preference", "Rank the cities by population size from largest to smallest", "Order the items by importance from most to least", "Rank the books in the order you read them", "Rank the colors by your favorite to least favorite"],
        "hypothetical": ["What would you do if you won the lottery", "In a hypothetical scenario, how would you react if you met a celebrity", "Imagine a situation where you find a wallet on the street", "What would be your response if you saw a UFO", "If you could time travel, where and when would you go"],
        "clarification": ["Could you please explain the concept of blockchain", "I need clarification on the fourth step of the process", "Can you provide more details about the theory of relativity", "Please explain the main idea of the book", "What is the meaning behind the artwork"],
        "leading": ["Don't you agree that exercise is important for a healthy lifestyle", "Isn't it true that honesty is the best policy", "Wouldn't you say that education is valuable", "Aren't you excited about the upcoming event", "Don't you think chocolate is delicious"],
        "critical-thinking": ["How would you solve the problem of climate change", "What are your thoughts on the impact of technology on society", "Can you critically analyze the economic implications of the policy", "What strategies would you use to improve customer satisfaction", "How do you propose to address the issue of poverty"],
        "reflective": ["How do you feel about your recent achievements", "Share your reflections on the past year", "What are your sentiments regarding the current political situation", "Reflect on your experiences during the trip", "How do you perceive the concept of success"]
    }

    # Check if the question_type is valid
    if question_type not in static_questions:
        raise ValueError("Invalid question_type. Supported values are: {}".format(", ".join(static_questions.keys())))

    # Initialize the initial prompt
    user_prompt = "In light of the given context, craft precisely {} pairs of prompts and their corresponding completions, following these guidelines for the context below:\n".format(num_questions)

    # Generate questions based on the specified type
    for i in range(1, num_questions + 1):
        questions = static_questions[question_type]
        if i <= len(questions):
            question = questions[i - 1] + "?"
        else:
            question = "Example {}: {} question {}".format(i, question_type.capitalize(), i)
        user_prompt += "Example {}: {}\n".format(i, question)

    # Add the remaining context
    user_prompt += "Each prompt is inherently correctly answerable but constructed to provoke an in-depth response.\n"
    user_prompt += "Each completion must be meticulously developed offering a sufficient explanation and ample arguments to justify the given response.\n"
    user_prompt += "All responses should be formatted within a JSON ARRAY structure.\n"
    user_prompt += "Each corresponding response should be meticulously crafted to offer a detailed explanation along with a robust argument to substantiate the response.\n"
    user_prompt += "Each individual JSON record should encapsulate one distinct prompt and its corresponding in-depth completion.\n"
    user_prompt += "The returned result MUST be formatted as JSON ARRAY structure:\n"
    user_prompt += "[\n"
    user_prompt += '    {"prompt": "question1", "completion": "answer1"},\n'
    user_prompt += '    {"prompt": "question2", "completion": "answer2"}\n'
    user_prompt += "]\n"
    user_prompt += "Context:\n"

    return user_prompt


def generate_prompt_completions(context_text: str, output_csv: str,
                                system_prompt: str = "You are an assistant to create question from a context", user_prompt: str = "",
                                openai_key: Optional[str] = None,
                                temperature: float = 1, model: str = "gpt-3.5-turbo",
                                max_tokens: int = 1054, top_p: float = 1,
                                frequency_penalty: float = 0, presence_penalty: float = 0,
                                retry_limit: int = 3,
                                num_questions: int = 3, question_type: str = "open-ended") -> List[Dict[str, str]]:
    """
    Generates prompt completions and saves them to a CSV file.

    Args:
        context_text (str): The context text.
        output_csv (str): The path to the output CSV file.
        system_prompt (str, optional): The system prompt. Defaults to "".
        user_prompt (str, optional): The initial user prompt. Defaults to "".
        openai_key (str, optional): The OpenAI API key. Defaults to None.
        temperature (float, optional): The temperature parameter. Defaults to 1.
        model (str, optional): The OpenAI model to use. Defaults to "gpt-3.5-turbo".
        max_tokens (int, optional): The maximum number of tokens. Defaults to 1054.
        top_p (float, optional): The top-p parameter. Defaults to 1.
        frequency_penalty (float, optional): The frequency penalty. Defaults to 0.
        presence_penalty (float, optional): The presence penalty. Defaults to 0.
        retry_limit (int, optional): The maximum number of retry attempts. Defaults to 3.
        num_questions (int, optional): The number of questions to generate. Defaults to 3.
        question_type (str, optional): The type of questions (e.g., "open-ended", "yes/no", "multiple-choice", etc.). Defaults to "open-ended".

    Returns:
    -------
    List[Dict[str, str]]:
        Returns a list of dictionaries with 'prompt' and 'completion' as keys.
    """
    # Load the OpenAI API key
    openai.api_key = openai_key or os.environ["OPENAI_API_KEY"]

    # Customize the initial prompt based on the number and type of questions
    user_prompt = generate_user_prompt(num_questions, question_type)

    user_prompt = user_prompt + context_text
    print(user_prompt)
    retry_count = 0

    while retry_count < retry_limit:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            break
        except openai.error.OpenAIError as e:
            retry_count += 1
            print(f"Retry attempt {retry_count} due to {e}. Trying again in 0.5 seconds...")
            time.sleep(RETRY_SLEEP_SECONDS)
        except openai.error.InvalidRequestError as e:
            # If the request fails due to invalid parameters, increment the retry counter, sleep for 0.5 seconds, and then try again
            retry_count += 1
            print(f"Retry attempt {retry_count} failed due to Invalid Request {e}. Max tokens = {max_tokens}. Trying again in 0.5 seconds...")
            max_tokens = int(max_tokens *0.8)
            time.sleep(RETRY_SLEEP_SECONDS)  # Pause for 0.5 seconds
        except openai.error.ServiceUnavailableError:
            # If the request fails due to service unavailability, sleep for 10 seconds and then try again without incrementing the retry counter
            print("\n\nService is currently unavailable. Waiting for 10 seconds before retrying...\n\n")
            time.sleep(10)  # Pause for 10 seconds
        except Exception as e:
            print("\n\nException: \n",e," \n\n")
            time.sleep(20)
            if retry_count == 3:
                print(f"Gave up after 3 attempts for context: {context_text}")
                continue

    # Process the response
    print(response)
    if 'choices' in response and len(response.choices) > 0:
        json_string = response.choices[0].message['content'].strip()
        # Parse the JSON string
        try:
            prompt_completion_pairs = json.loads(json_string)
            
            # Save to CSV
            list_to_save = [{"Prompt": pair["prompt"], "Completion": pair["completion"]} for pair in prompt_completion_pairs]
            list_to_csv(list_to_save, output_csv)

        except json.JSONDecodeError as e:
            print("JSON response:", json_string)
            print("Error decoding JSON response", e)
            return []

    return json_string
