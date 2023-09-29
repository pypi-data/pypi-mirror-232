import logging
import os

import litellm

from trulens_eval.feedback import prompts
from trulens_eval.feedback.provider.base import Provider
from trulens_eval.feedback.provider.endpoint import LiteLLMEndpoint
from trulens_eval.feedback.provider.endpoint.base import Endpoint
from trulens_eval.keys import set_openai_key
from trulens_eval.utils.generated import re_1_10_rating

logger = logging.getLogger(__name__)


class LiteLLM(Provider):
    """Out of the box feedback functions calling OpenAI APIs.
    """
    model_engine: str
    endpoint: Endpoint

    def __init__(
        self, *args, endpoint=None, model_engine="gpt-3.5-turbo", **kwargs
    ):
        # NOTE(piotrm): pydantic adds endpoint to the signature of this
        # constructor if we don't include it explicitly, even though we set it
        # down below. Adding it as None here as a temporary hack.
        """
        Create an LiteLLM Provider with out of the box feedback functions.

        **Usage:**
        ```
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        ```

        Args:
            model_engine (str): The LiteLLM completion model.Defaults to `gpt-3.5-turbo`
            endpoint (Endpoint): Internal Usage for DB serialization
        """
        # TODO: why was self_kwargs required here independently of kwargs?
        self_kwargs = dict()
        self_kwargs.update(**kwargs)
        self_kwargs['model_engine'] = model_engine
        self_kwargs['endpoint'] = LiteLLMEndpoint(*args, **kwargs)

        super().__init__(
            **self_kwargs
        )  # need to include pydantic.BaseModel.__init__

    def _create_chat_completion(self, *args, **kwargs):
        return litellm.completion(*args, **kwargs)

    def _find_relevant_string(self, full_source, hypothesis):
        return self.endpoint.run_me(
            lambda: self._create_chat_completion(
                model=self.model_engine,
                temperature=0.0,
                messages=[
                    {
                        "role":
                            "system",
                        "content":
                            str.format(
                                prompts.SYSTEM_FIND_SUPPORTING,
                                prompt=full_source,
                            )
                    }, {
                        "role":
                            "user",
                        "content":
                            str.format(
                                prompts.USER_FIND_SUPPORTING,
                                response=hypothesis
                            )
                    }
                ]
            )["choices"][0]["message"]["content"]
        )

    def _summarized_groundedness(self, premise: str, hypothesis: str) -> float:
        """ A groundedness measure best used for summarized premise against simple hypothesis.
        This LLM implementation uses information overlap prompts.

        Args:
            premise (str): Summarized source sentences.
            hypothesis (str): Single statement setnece.

        Returns:
            float: Information Overlap
        """
        return re_1_10_rating(
            self.endpoint.run_me(
                lambda: self._create_chat_completion(
                    model=self.model_engine,
                    temperature=0.0,
                    messages=[
                        {
                            "role":
                                "system",
                            "content":
                                str.format(
                                    prompts.LLM_GROUNDEDNESS,
                                    premise=premise,
                                    hypothesis=hypothesis,
                                )
                        }
                    ]
                )["choices"][0]["message"]["content"]
            )
        ) / 10

    def _groundedness_doc_in_out(
        self, premise: str, hypothesis: str, chain_of_thought=True
    ) -> str:
        """An LLM prompt using the entire document for premise and entire statement document for hypothesis

        Args:
            premise (str): A source document
            hypothesis (str): A statement to check

        Returns:
            str: An LLM response using a scorecard template
        """
        if chain_of_thought:
            system_prompt = prompts.LLM_GROUNDEDNESS_FULL_SYSTEM
        else:
            system_prompt = prompts.LLM_GROUNDEDNESS_SYSTEM_NO_COT
        return self.endpoint.run_me(
            lambda: self._create_chat_completion(
                model=self.model_engine,
                temperature=0.0,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    }, {
                        "role":
                            "user",
                        "content":
                            str.format(
                                prompts.LLM_GROUNDEDNESS_FULL_PROMPT,
                                premise=premise,
                                hypothesis=hypothesis
                            )
                    }
                ]
            )["choices"][0]["message"]["content"]
        )

    def _extract_score_and_reasons_from_response(
        self, system_prompt: str, user_prompt: str = None, normalize=10
    ):
        """Extractor for our LLM prompts. If CoT is used; it will look for "Supporting Evidence" template.
        Otherwise, it will look for the typical 1-10 scoring.

        Args:
            system_prompt (str): A pre-formated system prompt

        Returns:
            The score and reason metadata if available.
        """
        llm_messages = [{"role": "system", "content": system_prompt}]
        if user_prompt is not None:
            llm_messages.append({"role": "user", "content": user_prompt})

        response = self.endpoint.run_me(
            lambda: self._create_chat_completion(
                model=self.model_engine, temperature=0.0, messages=llm_messages
            )["choices"][0]["message"]["content"]
        )
        if "Supporting Evidence" in response:
            score = 0
            for line in response.split('\n'):
                if "Score" in line:
                    score = re_1_10_rating(line) / normalize
            return float(score), {"reason": response}
        else:
            return re_1_10_rating(response) / normalize

    def qs_relevance(self, question: str, statement: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the relevance of the statement to the question.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.qs_relevance).on_input_output() 
        ```
        The `on_input_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)
        
        Usage on RAG Contexts:
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.qs_relevance).on_input().on(
            TruLlama.select_source_nodes().node.text # See note below
        ).aggregate(np.mean) 

        ```
        The `on(...)` selector can be changed. See [Feedback Function Guide : Selectors](https://www.trulens.org/trulens_eval/feedback_function_guide/#selector-details)



        Args:
            question (str): A question being asked. 
            statement (str): A statement to the question.

        Returns:
            float: A value between 0 and 1. 0 being "not relevant" and 1 being "relevant".
        """
        system_prompt = str.format(
            prompts.QS_RELEVANCE, question=question, statement=statement
        )
        return self._extract_score_and_reasons_from_response(system_prompt)

    def qs_relevance_with_cot_reasons(
        self, question: str, statement: str
    ) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the relevance of the statement to the question.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.qs_relevance_with_cot_reasons).on_input_output() 
        ```
        The `on_input_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)
        
        Usage on RAG Contexts:
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.qs_relevance_with_cot_reasons).on_input().on(
            TruLlama.select_source_nodes().node.text # See note below
        ).aggregate(np.mean) 

        ```
        The `on(...)` selector can be changed. See [Feedback Function Guide : Selectors](https://www.trulens.org/trulens_eval/feedback_function_guide/#selector-details)



        Args:
            question (str): A question being asked. 
            statement (str): A statement to the question.

        Returns:
            float: A value between 0 and 1. 0 being "not relevant" and 1 being "relevant".
        """
        system_prompt = str.format(
            prompts.QS_RELEVANCE, question=question, statement=statement
        )
        system_prompt = system_prompt.replace(
            "RELEVANCE:", prompts.COT_REASONS_TEMPLATE
        )
        return self._extract_score_and_reasons_from_response(system_prompt)

    def relevance(self, prompt: str, response: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the relevance of the response to a prompt.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.relevance).on_input_output()
        ```
        The `on_input_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)


        Usage on RAG Contexts:
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.relevance).on_input().on(
            TruLlama.select_source_nodes().node.text # See note below
        ).aggregate(np.mean) 

        ```
        The `on(...)` selector can be changed. See [Feedback Function Guide : Selectors](https://www.trulens.org/trulens_eval/feedback_function_guide/#selector-details)


        Args:
            prompt (str): A text prompt to an agent. 
            response (str): The agent's response to the prompt.

        Returns:
            float: A value between 0 and 1. 0 being "not relevant" and 1 being "relevant".
        """
        system_prompt = str.format(
            prompts.PR_RELEVANCE, prompt=prompt, response=response
        )
        return self._extract_score_and_reasons_from_response(system_prompt)

    def relevance_with_cot_reasons(self, prompt: str, response: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the relevance of the response to a prompt.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.relevance_with_cot_reasons).on_input_output()
        ```
        The `on_input_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)


        Usage on RAG Contexts:
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.relevance_with_cot_reasons).on_input().on(
            TruLlama.select_source_nodes().node.text # See note below
        ).aggregate(np.mean) 

        ```
        The `on(...)` selector can be changed. See [Feedback Function Guide : Selectors](https://www.trulens.org/trulens_eval/feedback_function_guide/#selector-details)


        Args:
            prompt (str): A text prompt to an agent. 
            response (str): The agent's response to the prompt.

        Returns:
            float: A value between 0 and 1. 0 being "not relevant" and 1 being "relevant".
        """
        system_prompt = str.format(
            prompts.PR_RELEVANCE, prompt=prompt, response=response
        )
        system_prompt = system_prompt.replace(
            "RELEVANCE:", prompts.COT_REASONS_TEMPLATE
        )
        return self._extract_score_and_reasons_from_response(system_prompt)

    def sentiment(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the sentiment of some text.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.sentiment).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): Text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "negative sentiment" and 1 being "positive sentiment".
        """
        system_prompt = prompts.SENTIMENT_SYSTEM_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def sentiment_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the sentiment of some text.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.sentiment_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): Text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "negative sentiment" and 1 being "positive sentiment".
        """

        system_prompt = prompts.SENTIMENT_SYSTEM_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def model_agreement(self, prompt: str, response: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that gives Chat GPT the same
        prompt and gets a response, encouraging truthfulness. A second template
        is given to Chat GPT with a prompt that the original response is
        correct, and measures whether previous Chat GPT's response is similar.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.model_agreement).on_input_output() 
        ```
        The `on_input_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        
        Args:
            prompt (str): A text prompt to an agent. 
            response (str): The agent's response to the prompt.

        Returns:
            float: A value between 0 and 1. 0 being "not in agreement" and 1 being "in agreement".
        """
        logger.warning(
            "model_agreement has been deprecated. Use GroundTruthAgreement(ground_truth) instead."
        )
        oai_chat_response = self.endpoint.run_me(
            lambda: self._create_chat_completion(
                model=self.model_engine,
                temperature=0.0,
                messages=[
                    {
                        "role": "system",
                        "content": prompts.CORRECT_SYSTEM_PROMPT
                    }, {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )["choices"][0]["message"]["content"]
        )
        agreement_txt = self._get_answer_agreement(
            prompt, response, oai_chat_response, self.model_engine
        )
        return re_1_10_rating(agreement_txt) / 10

    def conciseness(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the conciseness of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.conciseness).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)


        Args:
            text (str): Text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "not concise" and 1 being "concise".
        """

        system_prompt = prompts.LANGCHAIN_CONCISENESS_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def correctness(self, text: str) -> float:
        """
       Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the correctness of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.correctness).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): Text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "not correct" and 1 being "correct".
        """

        system_prompt = prompts.LANGCHAIN_CORRECTNESS_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def correctness_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the correctness of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.correctness_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): Text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "not correct" and 1 being "correct".
        """

        system_prompt = prompts.LANGCHAIN_CORRECTNESS_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def coherence(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the coherence of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.coherence).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)


        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "not coherent" and 1 being "coherent".
        """
        system_prompt = prompts.LANGCHAIN_COHERENCE_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def coherence_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the coherence of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.coherence_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)


        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "not coherent" and 1 being "coherent".
        """
        system_prompt = prompts.LANGCHAIN_COHERENCE_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def harmfulness(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the harmfulness of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.harmfulness).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        
        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "harmful" and 1 being "not harmful".
        """
        system_prompt = prompts.LANGCHAIN_HARMFULNESS_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def harmfulness_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the harmfulness of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.harmfulness_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        
        Args:
            text (str): The text to evaluate.


        Returns:
            float: A value between 0 and 1. 0 being "harmful" and 1 being "not harmful".
        """

        system_prompt = prompts.LANGCHAIN_HARMFULNESS_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def maliciousness(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the maliciousness of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.maliciousness).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        
        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "malicious" and 1 being "not malicious".
        """
        system_prompt = prompts.LANGCHAIN_MALICIOUSNESS_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def maliciousness_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the maliciousness of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.maliciousness_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        
        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "malicious" and 1 being "not malicious".
        """
        system_prompt = prompts.LANGCHAIN_MALICIOUSNESS_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def helpfulness(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the helpfulness of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.helpfulness).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)
        
        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "not helpful" and 1 being "helpful".
        """
        system_prompt = prompts.LANGCHAIN_HELPFULNESS_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def helpfulness_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the helpfulness of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.helpfulness_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)
        
        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "not helpful" and 1 being "helpful".
        """

        system_prompt = prompts.LANGCHAIN_HELPFULNESS_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def controversiality(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the controversiality of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.controversiality).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)
        
        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "controversial" and 1 being "not controversial".
        """
        system_prompt = prompts.LANGCHAIN_CONTROVERSIALITY_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def controversiality_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the controversiality of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.controversiality_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)
        
        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "controversial" and 1 being "not controversial".
        """
        system_prompt = prompts.LANGCHAIN_CONTROVERSIALITY_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def misogyny(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the misogyny of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.misogyny).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "misogynist" and 1 being "not misogynist".
        """
        system_prompt = prompts.LANGCHAIN_MISOGYNY_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def misogyny_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the misogyny of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.misogyny_with_cot_reasons).on_output() 
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "misogynist" and 1 being "not misogynist".
        """
        system_prompt = prompts.LANGCHAIN_MISOGYNY_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def criminality(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the criminality of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.criminality).on_output()
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "criminal" and 1 being "not criminal".

        """
        system_prompt = prompts.LANGCHAIN_CRIMINALITY_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def criminality_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the criminality of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.criminality_with_cot_reasons).on_output()
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "criminal" and 1 being "not criminal".
        """

        system_prompt = prompts.LANGCHAIN_CRIMINALITY_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def insensitivity(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the insensitivity of some text. Prompt credit to Langchain Eval.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.insensitivity).on_output()
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "insensitive" and 1 being "not insensitive".
        """
        system_prompt = prompts.LANGCHAIN_INSENSITIVITY_PROMPT
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def insensitivity_with_cot_reasons(self, text: str) -> float:
        """
        Uses a chat completion model accessed through LiteLLM's interface. A function that completes a
        template to check the insensitivity of some text. Prompt credit to Langchain Eval.
        Also uses chain of thought methodology and emits the reasons.

        **Usage:**
        ```
        from trulens_eval import Feedback
        from trulens_eval.feedback.provider.litellm import LiteLLM
        litellm_provider = LiteLLM()

        feedback = Feedback(litellm_provider.insensitivity_with_cot_reasons).on_output()
        ```
        The `on_output()` selector can be changed. See [Feedback Function Guide](https://www.trulens.org/trulens_eval/feedback_function_guide/)

        Args:
            text (str): The text to evaluate.

        Returns:
            float: A value between 0 and 1. 0 being "insensitive" and 1 being "not insensitive".
        """

        system_prompt = prompts.LANGCHAIN_INSENSITIVITY_PROMPT
        system_prompt = system_prompt + prompts.COT_REASONS_TEMPLATE
        return self._extract_score_and_reasons_from_response(
            system_prompt, user_prompt=text
        )

    def _get_answer_agreement(
        self, prompt, response, check_response, model_engine="gpt-3.5-turbo"
    ):
        llm_chat_response = self.endpoint.run_me(
            lambda: self._create_chat_completion(
                model=model_engine,
                temperature=0.0,
                messages=[
                    {
                        "role":
                            "system",
                        "content":
                            prompts.AGREEMENT_SYSTEM_PROMPT %
                            (prompt, response)
                    }, {
                        "role": "user",
                        "content": check_response
                    }
                ]
            )["choices"][0]["message"]["content"]
        )
        return llm_chat_response