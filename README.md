# Claim Tree is all you need

This Idea has been sitting in my head for many years. And as I was now forced to do group AI assigment thankfully of my choice, I decided to finally put in in code.

The system consists of two key components:

•	Large Language Model (LLM) for claim context generation
•	Tree-like database of debunked claims

First, a large pre-trained language model such as GPT is used to generate contextual information for the input claim. The claim is fed into the LLM along with relevant metadata, including author, date, and platform. The LLM outputs a summary containing information in a fixed order: “who”, “when”, “where”, “what”, and “why”. An example vector could be:

•	Who: Joe Smith (“Who” is another tree with a calculated trust score based on all historical sub-claims)
•	When: 03/05/2021
•	Where: Twitter (“Where” is another tree with a calculated trust score based on all historical sub-claims)
•	What: COVID-19 vaccines are unsafe
•	Why:
-	Vaccines developed too quickly.
-	Adverse reactions are being covered up.

Finally, this summary is converted to an embedding and then compared with a vector database of debunked claims using a semantic search. Then we calculate trust by evaluating the trust score, going through all the fields and claims for each sub-claim.

5.1 Embeddings

The task of the LLM is to transform the input with its context into a summary in the following format:

•	Who: the author or originator of the claim. This is also stored in the database as a separate claim tree that is used during trust score calculations. 
•	When: the date the claim was made. The temporal information is important so that the semantic search returns results for the correct date range.
•	Where: the platform or medium where the claim appeared. Also stored as a separate claim tree. It is relevant for assessing the trust and track record of the source.
•	What: a summarised version of the primary assertion or allegation made in the claim.
•	Why: the list of supporting claims. Also stored as separate claim trees. Typically, evidence is provided to strengthen the main claim, which is critical for hierarchical trust calculation.

Through few-shot prompt priming, the model can relatively efficiently extract requested summaries.

5.2 Database

Each claim often has supporting sub-claims in the “who” parameter, which is important for the trust calculation. Now, let's explore the following example:

	Claim: “what”: Vaccines are unsafe (“who”: Website A, Calculated Trust: 0.01)
	Claim: “what”: Vaccines contain toxic ingredients (“who”: Website B, Calculated Trust: 0.07)
	Claim: “what”: Vaccines contain mercury (“who”: Website C, Calculated Trust: 0.001)
	Claim: “what”: Vaccines don’t contain mercury (“who”: World Health Organization, Calculated Trust: 0.9)
	Claim: “what”: Mercury was removed from vaccines in 1999 (“who”: Scientific Study, Calculated Trust: 0.95)

5.3 Calculating trust

The maximum achievable trust score for any claim should be restricted by the variety of dates and the number of sub-claims. The trustworthiness of the top claim depends on the trustworthiness of its supporting evidence and the trust of the source of the main claim. This approach helps in identifying and mitigating the spread of misinformation in a more robust and balanced way. Most importantly, trust in the “who” that is a claim information source, is not hard-coded, but dictated by mathematics and dynamically calculated, thus markedly reducing the bias built into the model.
Consider the example of reputable sources like Reuters or the Nature Journal. The median time of their existence is typically not measured in seconds, their historical claim count is not limited to 1. But their overall trust will be calculated from the combined credibility of published academics or journalists, and this would be significantly higher than, for example, typical anonymous internet sources. Hence, the high trust assigned to Reuters as a “who” source must be earned. And it must be earned with each new claim. It's essential to acknowledge that times change, and even once reputable organisations sadly change too. This simple transparent dynamic calculation of trust ensures that no bias is encoded in the model making such important decisions. The credibility of a source is thus continuously updated and accurately reflects its reliability based on the latest information. This will provide a more nuanced and accurate measure of trust compared to a static, hard-coded value. This approach helps in maintaining the integrity of the fact-checking process.

5.4 Claim history

If the trustworthiness of any claim is deemed only as low as the lowest historically achieved trust for any sub-claim is perhaps too harsh and can lead to “vanishing gradient” kind of problems”. A more conservative approach, such as using a median or average trust value, may be needed. Since even typically reliable sources like the BBC or WHO make mistakes. While it's crucial not to undermine their hard journalistic efforts, it's equally important not to set them in stone as the ultimate source of truth. But to consider them in the median of sub-claims, it is essential to check the relevance of all these sub-claims to the claim itself and ensure that they relate to the same topic. 
Why is this important? Attaching a falsehood to two potentially unrelated truths is a recognised and frequently employed misinformation tactic aimed at manipulating the masses. Perhaps using the median calculation is recommended only for the top-level children within the “who” claim tree. For all other claim node propagations up the tree, a straightforward multiplication with the trust value of the least trusted child could lead to a more balanced trust assessment, but this remains to be tested. 

5.5 Possible real-time fact-checking

Our specific goal is to always update the context for each debate participant. Essentially, it is a text with a summary that contains “who”, “when”, “where”, “what”, and “why”. This information is then inserted after the mentioned sentence, serving as a reference to the debate's transcript. The aim is to build a chain of thought from a series of fact-checked claims. To achieve this, I recalculate the trust of each new sentence. This is done by matching the summary of the whole chain of claims for that user against the claim tree. The result can be presented in the form of simple color-coded status messages for each participant's last claim, indicating whether it is considered true (green), questionable (yellow), or false (red) based on the context of what they have said so far.

5.6 Trust chains in live debates

By maintaining up-to-date context for each debate participant and independently fact-checking their claims within their respective chains of thought, we can use the power of LLM. This allows us to ask general reasoning questions, such as:

•	Is the following chain of thought reasonable?
•	What is indirectly implied?
•	What is the inferred intent of Participant 1?

We append the accumulated debate transcript, instrumenting it with trust scores that are calculated and captured after each claim. This would continuously provide the model with insights into the trustworthiness of these claims and participants as a rolling number.
