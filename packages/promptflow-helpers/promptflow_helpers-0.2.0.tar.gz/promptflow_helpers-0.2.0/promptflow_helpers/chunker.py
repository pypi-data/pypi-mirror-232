import nltk  # type: ignore
from typing import List
from pydantic import BaseModel

from promptflow_helpers.helpers import num_tokens_from_string


class SentenceInfo(BaseModel):
    text: str
    num_tokens: int
    start_cursor: int
    end_cursor: int


class ChunkInfo(BaseModel):
    text: str
    num_tokens: int
    start_cursor: int
    end_cursor: int
    chunk_index: int


def get_sentence_infos(
    text: str, token_encoding_name: str = "cl100k_base", language: str = "dutch"
) -> List[SentenceInfo]:
    """
    Tokenizes the given text into sentences using NLTK and returns information about each sentence.

    The returned information for each sentence includes:
    - The number of tokens in the sentence.
    - The start index (cursor) of the sentence in the original text.
    - The end index (cursor) of the sentence in the original text.

    Parameters:
    - text (str): The input text to tokenize and analyze.
    - token_encoding_name (str, optional): The name of the token encoding to use.
    Default is "cl100k_base", which is the same tokenization as GPT-3.5 turbo and GPT-4.

    Returns:
    - List[SentenceInfo]: A list of SentenceInfo objects,
    each containing information about a single sentence in the text.
    """
    sentences = nltk.sent_tokenize(text, language=language)

    sentence_infos: List[SentenceInfo] = []
    start_ind = 0

    for sentence in sentences:
        num_tokens = num_tokens_from_string(sentence, encoding_name=token_encoding_name)
        sent_start = text.find(sentence, start_ind)
        sentence_infos.append(
            SentenceInfo(
                text=sentence,
                num_tokens=num_tokens,
                start_cursor=sent_start,
                end_cursor=sent_start + len(sentence),
            )
        )

        start_ind = sent_start + len(sentence)

    return sentence_infos


def split_long_sentence(
    si: SentenceInfo, overlap: int, wanted_tokens: int, token_encoding_name: str
) -> List[SentenceInfo]:
    """
    Split a long sentence into multiple chunks based on a specified token limit, with a defined overlap between chunks.

    Args:
    - si (SentenceInfo): An instance containing the sentence to be split along
    with its metadata (start and end cursors, number of tokens).
    - overlap (int): The number of overlapping characters desired between consecutive chunks.
    - wanted_tokens (int): The maximum number of tokens desired for each chunk.
    - token_encoding_name (str): The encoding name to be used when counting the number of tokens in a string.

    Returns:
    - List[SentenceInfo]: A list of SentenceInfo instances for each chunk.
    Each instance contains the chunk's text and metadata.

    Notes:
    - If the original sentence's token count is less than `wanted_tokens`,
    the function returns a list containing only the original SentenceInfo.
    - If splitting the sentence results in chunks that differ in token count,
    the function chooses the split with the smallest difference.
    - Overlaps are adjusted at the beginning and end of the original
    sentence so that chunks do not exceed the boundaries of the original sentence.
    """
    total_tokens = si.num_tokens

    floor_num_chunks = total_tokens // wanted_tokens
    ceil_num_chunks = floor_num_chunks + 1

    if floor_num_chunks == 0:
        return [si]

    dist_floor = total_tokens / floor_num_chunks - wanted_tokens
    dist_top = wanted_tokens - total_tokens / ceil_num_chunks

    num_chunks = floor_num_chunks if dist_floor < dist_top else ceil_num_chunks

    if num_chunks == 1:
        return [si]

    sent_len = len(si.text)
    step = sent_len // num_chunks + 1

    split_sentence_infos: List[SentenceInfo] = []

    # we start our cursor at index 0 and later adjust it based on the start_cursor of the original sentence_info
    for cursor in range(0, sent_len - overlap, step):
        start_cursor = max(0, cursor - overlap)
        end_cursor = min(cursor + step + overlap, sent_len)
        sentence = si.text[start_cursor:end_cursor]
        num_tokens = num_tokens_from_string(sentence, encoding_name=token_encoding_name)

        split_sentence_infos.append(
            SentenceInfo(
                text=sentence,
                num_tokens=num_tokens,
                start_cursor=max(si.start_cursor, start_cursor + si.start_cursor),
                end_cursor=min(end_cursor + si.start_cursor, si.end_cursor),
            )
        )

    return split_sentence_infos


def _get_current_chunk_tokens(si_list: List[SentenceInfo]) -> int:
    return sum(si.num_tokens for si in si_list)


def _sentence_infos_to_chunk_info(
    si_list: List[SentenceInfo], chunk_index: int
) -> ChunkInfo:
    return ChunkInfo(
        text=" ".join(si.text for si in si_list),
        num_tokens=sum(si.num_tokens for si in si_list),
        start_cursor=si_list[0].start_cursor,
        end_cursor=si_list[-1].end_cursor,
        chunk_index=chunk_index,
    )


def _add_sentence_infos_to_chunk(si_list: List[SentenceInfo], chunk: ChunkInfo) -> None:
    extra_chunk_info = _sentence_infos_to_chunk_info(si_list, 0)
    chunk.text += " " + extra_chunk_info.text
    chunk.num_tokens += extra_chunk_info.num_tokens
    chunk.end_cursor = extra_chunk_info.end_cursor


def _add_overlap_to_chunks(
    chunk_infos: List[ChunkInfo], full_text: str, overlap: int, encoding_name: str
) -> None:
    for ci in chunk_infos:
        new_start_cursor = max(0, ci.start_cursor - overlap)
        new_end_cursor = min(len(full_text), ci.end_cursor + overlap)
        ci.text = full_text[new_start_cursor:new_end_cursor]
        ci.start_cursor = new_start_cursor
        ci.end_cursor = new_end_cursor
        ci.num_tokens = num_tokens_from_string(ci.text, encoding_name)


def get_chunk_infos(
    text: str,
    wanted_tokens: int,
    split_sentence_overlap_characters: int = 0,
    chunk_overlap_characters: int = 0,
    token_encoding_name: str = "cl100k_base",
) -> List[ChunkInfo]:
    """
    Splits the given text into chunks where each chunk has approximately the desired number of tokens.

    This function first divides the text into sentences using `get_sentence_infos`. Sentences that
    have more tokens than the desired number of tokens per chunk (especially if they exceed 4/3
    of the wanted tokens) are further split using `split_long_sentence`.

    Parameters:
    - text (str): The input text to be chunked.
    - wanted_tokens (int): The desired number of tokens for each chunk. The actual number of tokens
      in a chunk might differ to make sure sentences are not broken inappropriately.
    - split_sentence_overlap_characters (int, optional): The number of overlapping characters
      desired between consecutive sentence splits. Default is 0.
    - chunk_overlap_characters (int, optional): The number of overlapping characters desired
      between consecutive chunks. Default is 0.
    - token_encoding_name (str, optional): The encoding name to be used when counting the number
      of tokens in a string. Default is "cl100k_base".

    Returns:
    - List[ChunkInfo]: A list of ChunkInfo objects, where each object contains information about a
      chunk including its text, number of tokens, start and end cursors, and chunk index.

    Notes:
    - The function tries to avoid splitting sentences unnecessarily. If adding a sentence to a chunk
      results in exceeding the wanted_tokens limit, a decision is made based on which option brings
      the chunk's total tokens closer to the wanted_tokens (either by including or excluding the sentence).
    - The function also manages overlap between chunks or split sentences to ensure context continuity
      while maintaining the desired token limit as close as possible.
    """
    sentence_infos: List[SentenceInfo] = get_sentence_infos(text, token_encoding_name)

    # Split long sentences into smaller ones
    sentence_infos_split: List[SentenceInfo] = []
    for sent_info in sentence_infos:
        if sent_info.num_tokens > 4 / 3 * wanted_tokens:
            split_sis: List[SentenceInfo] = split_long_sentence(
                sent_info,
                split_sentence_overlap_characters,
                wanted_tokens,
                token_encoding_name,
            )
            sentence_infos_split += split_sis
        else:
            sentence_infos_split.append(sent_info)

    chunk_infos: List[ChunkInfo] = []
    current_chunk: List[SentenceInfo] = []
    chunk_index = 0

    for i in range(len(sentence_infos_split)):
        sent_info = sentence_infos_split[i]
        current_chunk_tokens = _get_current_chunk_tokens(current_chunk)

        if current_chunk_tokens + sent_info.num_tokens > wanted_tokens:
            # Decide if we add the current sentence to the current chunk or the next chunk.
            dist_add = current_chunk_tokens + sent_info.num_tokens - wanted_tokens
            dist_no_add = wanted_tokens - current_chunk_tokens
            if dist_add < dist_no_add:
                # add to current chunk
                current_chunk.append(sent_info)

                chunk_infos.append(
                    _sentence_infos_to_chunk_info(current_chunk, chunk_index)
                )
                current_chunk = []
            else:
                # add to next chunk
                chunk_infos.append(
                    _sentence_infos_to_chunk_info(current_chunk, chunk_index)
                )
                current_chunk = [sent_info]
            chunk_index += 1
        else:
            current_chunk.append(sent_info)

    if not current_chunk:
        return chunk_infos

    # If we have a current_chunk left, decide if we add it to the last chunk or make it a new chunk
    if not chunk_infos:
        chunk_infos.append(_sentence_infos_to_chunk_info(current_chunk, chunk_index))
    else:
        current_chunk_tokens = _get_current_chunk_tokens(current_chunk)

        dist_add = current_chunk_tokens + chunk_infos[-1].num_tokens - wanted_tokens
        dist_no_add = wanted_tokens - current_chunk_tokens

        if dist_add < dist_no_add:
            _add_sentence_infos_to_chunk(current_chunk, chunk_infos[-1])
        else:
            chunk_infos.append(
                _sentence_infos_to_chunk_info(current_chunk, chunk_index)
            )

    if chunk_overlap_characters:
        _add_overlap_to_chunks(
            chunk_infos, text, chunk_overlap_characters, token_encoding_name
        )

    return chunk_infos
