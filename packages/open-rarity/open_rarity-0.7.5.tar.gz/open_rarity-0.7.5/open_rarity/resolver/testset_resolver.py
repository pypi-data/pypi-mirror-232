import argparse
import csv
import io
import json
import logging
import math
import os
import pkgutil
from dataclasses import dataclass
from time import strftime, time
from typing import Iterable

import numpy as np

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_rarity import TokenRarity
from open_rarity.rarity_ranker import RarityRanker
from open_rarity.resolver.models.collection_with_metadata import CollectionWithMetadata
from open_rarity.resolver.models.token_with_rarity_data import (
    RankProvider,
    RarityData,
    TokenWithRarityData,
)
from open_rarity.resolver.opensea_api_helpers import (
    get_collection_with_metadata_from_opensea,
)
from open_rarity.resolver.rarity_providers.external_rarity_provider import (
    EXTERNAL_RANK_PROVIDERS,
    ExternalRarityProvider,
)
from open_rarity.scoring.handlers.arithmetic_mean_scoring_handler import (
    ArithmeticMeanScoringHandler,
)
from open_rarity.scoring.handlers.geometric_mean_scoring_handler import (
    GeometricMeanScoringHandler,
)
from open_rarity.scoring.handlers.harmonic_mean_scoring_handler import (
    HarmonicMeanScoringHandler,
)
from open_rarity.scoring.handlers.information_content_scoring_handler import (
    InformationContentScoringHandler,
)
from open_rarity.scoring.handlers.sum_scoring_handler import SumScoringHandler
from open_rarity.scoring.token_feature_extractor import TokenFeatureExtractor

harmonic_handler = HarmonicMeanScoringHandler()
arithmetic_handler = ArithmeticMeanScoringHandler()
geometric_handler = GeometricMeanScoringHandler()
sum_handler = SumScoringHandler()
ic_handler = InformationContentScoringHandler()

RankScore = tuple[int, float]
# Token ID -> Score
ScoredTokens = dict[int, float]
# Token ID -> Rank + Score
RankedTokens = dict[int, RankScore]

logger = logging.getLogger("open_rarity_logger")


parser = argparse.ArgumentParser()
parser.add_argument(
    "resolve_external_rarity",
    type=str,
    default="external",
    help="Specify 'external' if you want to resolve rarity from external providers",
)
parser.add_argument(
    "--cache",
    dest="cache_fetched_data",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="Whether we use local data files to cache external trait + rank data",
)
parser.add_argument(
    "--filename",
    dest="filename",
    default="test_collections.json",
    help="File in /data folder containing collections to resolve.",
)

# The fastest external rarity provider, taking <15 seconds to resolve all rank data.
parser.add_argument(
    "--rarity_sniffer",
    dest="fetch_rarity_sniffer",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="If external is specified, fetches rarity sniffer ranking data",
)

# Default disabled due to API key requirements. Without caching, this can take
# ~10 minutes for a 10k collection due to rate limits.
parser.add_argument(
    "--trait_sniper",
    dest="fetch_trait_sniper",
    action=argparse.BooleanOptionalAction,
    default=False,
    help=(
        "If external is specified, fetches trait sniper ranking data. "
        "If True, must set TRAIT_SNIPER_API_KEY env var."
    ),
)

# Default disabled because no public bulk fetcher function and therefore
# takes a long to fetch data for (~25 min for 10k collection).
parser.add_argument(
    "--rarity_sniper",
    dest="fetch_rarity_sniper",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="If external is specified, fetches rarity sniper ranking data",
)


@dataclass
class OpenRarityScores:
    arithmetic_scores: RankedTokens
    geometric_scores: RankedTokens
    harmonic_scores: RankedTokens
    sum_scores: RankedTokens
    information_content_scores: RankedTokens


def get_tokens_with_rarity(
    collection_with_metadata: CollectionWithMetadata,
    external_rank_providers: list[RankProvider] = EXTERNAL_RANK_PROVIDERS,
    resolve_remote_rarity: bool = True,
    batch_size: int = 300,
    max_tokens_to_calculate: int = None,
    cache_external_ranks: bool = True,
) -> list[TokenWithRarityData]:
    """Resolves assets through OpenSea API asset endpoint and turns them
    into token with rarity data, augmented with rankings from Gem, RaritySniper
    and TraitSniper.

    Parameters
    ----------
    collection : Collection
        collection
    resolve_remote_rarity : bool
        True if we need to resolve rarity ranks from
        external providers , False if not
    max_tokens_to_calculate (int, optional): If specified only gets ranking
        data of first `max_tokens`. Defaults to None.
    cache_external_ranks : bool
        If set to true, will cache external ranks into local json file and
        optionally use cached data if file exists. If cache file already exists,
        will not refetch or rewrite cache data.

    Returns
    -------
    list[TokenWithRarityData]
        provide list of tokens augmented with assets metadata and ranking provider
    """
    slug = collection_with_metadata.opensea_slug
    external_rarity_provider = ExternalRarityProvider()
    total_supply = min(
        max_tokens_to_calculate or collection_with_metadata.token_total_supply,
        collection_with_metadata.token_total_supply,
    )
    num_batches = math.ceil(total_supply / batch_size)
    tokens = collection_with_metadata.collection.tokens
    if len(tokens) != collection_with_metadata.token_total_supply:
        # TODO [open-rarity] - Add support for collections with skipped token ids
        msg = (
            f"Warning: Collection {slug} has {len(tokens)} tokens, but total supply "
            f"is {collection_with_metadata.token_total_supply}. This can happen if "
            f"the collection skips token IDs. "
        )
        logger.warning(msg)
        print(msg)
    tokens_with_rarity: list[TokenWithRarityData] = []

    t1_start = time()

    tokens_batch: Iterable[Token]
    for batch_id, tokens_batch in enumerate(
        np.array_split(tokens, num_batches)  # type: ignore
    ):
        message = (
            f"\tStarting batch {batch_id} for collection "
            f"{slug}: Processing {len(tokens_batch)} tokens. "
            f"Last token: {tokens_batch[-1]}"
        )
        logger.debug(message)
        print(message)

        # We will store all rarities calculated across providers in this list
        tokens_rarity_batch = [
            TokenWithRarityData(token=t, rarities=[]) for t in tokens_batch
        ]

        if resolve_remote_rarity:
            external_rarity_provider.fetch_and_update_ranks(
                collection_with_metadata=collection_with_metadata,
                tokens_with_rarity=tokens_rarity_batch,
                rank_providers=external_rank_providers,
                cache_external_ranks=cache_external_ranks,
            )
        # Add the batch of augmented tokens with rarity into return value
        tokens_with_rarity.extend(tokens_rarity_batch)

    t1_stop = time()
    logger.debug(
        "Elapsed time during the asset resolution in seconds {seconds}".format(
            seconds=t1_stop - t1_start
        )
    )

    return tokens_with_rarity


def resolve_collection_data(
    resolve_remote_rarity: bool,
    external_rank_providers: list[RankProvider],
    package_path: str = "open_rarity.data",
    filename: str = "test_collections.json",
    max_tokens_to_calculate: int = None,
    use_cache: bool = True,
    output_file_to_disk: bool = True,
) -> list | None:
    """Resolves collection information through OpenSea API

    Parameters
    ----------
    resolve_remote_rarity : bool
        Set to true to resolve external rarity ranks for rank comparisons
    package_path : str, optional
        The package path for where the collection data to resolve collection data lives,
        by default "open_rarity.data"
    filename : str, optional
        The filename of the file holding the collection slugs to resolve,
        by default "test_collections.json"
    max_tokens_to_calculate : int, optional
        If specified only gets ranking data of first `max_tokens`, by default None.
        Note: If this is provided, we cannot calculate OpenRarity ranks since
        it must be calculated after calculating scoring for entire collection.
    use_cache: bool
        If set to true, will cache fetched data from external API's in order to ensure
        re-runs for same collections are faster. Only use if collection and token
        metadata is static - do not work for unrevealed/changing collections.
    output_file_to_disk: bool
        If set to true, will output the resolved collection data to disk.
        Set to False if you want to use the data in memory only.
        Needed for testing.

    Returns
    -------
    list
        A list of the rows that would be written to the output file. Only returned if
        output_file_to_disk is set to False.

    Raises
    ------
    ValueError
        If the file containing collection slugs to resolve does not exist.
    """
    golden_collections = pkgutil.get_data(package_path, filename)
    if not golden_collections:
        raise ValueError("Can't resolve golden collections data file.")

    data = json.load(io.BytesIO(golden_collections))
    print("------------------------------")
    output_rows: list = []
    for collection_def in data:
        start_time = time()
        opensea_slug = collection_def["collection_slug"]
        print(f"\nBEGIN: Resolving collection {opensea_slug}")
        print(
            f"1. Fetching collection & token traits for: {opensea_slug} from opensea."
        )
        # Fetch collection metadata and tokens that belong to this collection
        # from opensea and other external api's.
        collection_with_metadata = get_collection_with_metadata_from_opensea(
            opensea_collection_slug=opensea_slug,
            use_cache=use_cache,
        )
        print(f"2. Fetching external rarity ranks for: {opensea_slug}")
        tokens_with_rarity: list[TokenWithRarityData] = get_tokens_with_rarity(
            collection_with_metadata=collection_with_metadata,
            resolve_remote_rarity=resolve_remote_rarity,
            max_tokens_to_calculate=max_tokens_to_calculate,
            cache_external_ranks=use_cache,
            external_rank_providers=external_rank_providers,
        )
        print(f"3. Calculating OpenRarity ranks for: {opensea_slug}")

        collection = collection_with_metadata.collection

        if max_tokens_to_calculate is None:
            assert collection.token_total_supply == len(tokens_with_rarity)
        else:
            assert max_tokens_to_calculate == len(tokens_with_rarity)

        # Calculate and append open rarity scores
        if max_tokens_to_calculate is None:
            open_rarity_scores = resolve_open_rarity_score(
                collection, collection.tokens
            )
            augment_with_open_rarity_scores(
                tokens_with_rarity=tokens_with_rarity,
                scores=open_rarity_scores,
            )

        if output_file_to_disk:
            print(f"4. Wrote to CSV: {opensea_slug}")

        rows = serialize_to_csv(
            collection_with_metadata=collection_with_metadata,
            tokens_with_rarity=tokens_with_rarity,
            dry_run=not output_file_to_disk,
        )
        if rows is not None:
            output_rows += rows
        time_elapsed = round(time() - start_time)
        print(f"FINISHED: Resolved collection: {opensea_slug} in {time_elapsed} secs")

    return output_rows if not output_file_to_disk else None


def augment_with_open_rarity_scores(
    tokens_with_rarity: list[TokenWithRarityData], scores: OpenRarityScores
) -> None:
    """Augments tokens_with_rarity with ranks and scores computed by
    OpenRarity scorers'"""
    for token_with_rarity in tokens_with_rarity:
        token_id = token_with_rarity.token.token_identifier.token_id  # type: ignore

        token_with_rarity.rarities.extend(
            [
                RarityData(
                    provider=RankProvider.OR_ARITHMETIC,
                    rank=scores.arithmetic_scores[token_id][0],
                    score=scores.arithmetic_scores[token_id][1],
                ),
                RarityData(
                    provider=RankProvider.OR_GEOMETRIC,
                    rank=scores.geometric_scores[token_id][0],
                    score=scores.geometric_scores[token_id][1],
                ),
                RarityData(
                    provider=RankProvider.OR_HARMONIC,
                    rank=scores.harmonic_scores[token_id][0],
                    score=scores.harmonic_scores[token_id][1],
                ),
                RarityData(
                    provider=RankProvider.OR_SUM,
                    rank=scores.sum_scores[token_id][0],
                    score=scores.sum_scores[token_id][1],
                ),
                RarityData(
                    provider=RankProvider.OR_INFORMATION_CONTENT,
                    rank=scores.information_content_scores[token_id][0],
                    score=scores.information_content_scores[token_id][1],
                ),
            ]
        )


def extract_rank(tokens_to_score: dict[str, TokenRarity]) -> RankedTokens:
    """Sorts dictionary by float score and extract rank according to the score

    Parameters
    ----------
    token_id_to_scores : dict[str, TokenRarity]
        dictionary of token_id_to_scores with token_id to score mapping

    Returns
    -------
    dict[str, RankScore]
        dictionary of token to rank, score pair
    """
    ranked_tokens: list[TokenRarity] = RarityRanker.set_rarity_ranks(
        token_rarities=list(tokens_to_score.values())
    )

    result = {}
    for token in ranked_tokens:
        assert token.rank
        # note: this is a bug, ignoring the mypy error for now
        # token_identifier can be of type SolanaMintAddressTokenIdentifier
        # which has no token_id
        result[int(token.token.token_identifier.token_id)] = (  # type: ignore
            token.rank,
            token.score,
        )
    return result


def resolve_open_rarity_score(
    collection: Collection, tokens: list[Token]
) -> OpenRarityScores:
    """Resolve scores from all scorers with trait_normalization

    Parameters
    ----------
    collection : Collection
        collection is needed since the score is based on the invdividual's traits
        probability across the entire collection
    tokens: Subset of tokens belonging to Collection to resolve open rarity scores for

    """
    t1_start = time()

    # Dictionaries of token IDs to their respective TokenRarity for each strategy
    arthimetic_dict: dict[str, TokenRarity] = {}
    geometric_dict: dict[str, TokenRarity] = {}
    harmonic_dict: dict[str, TokenRarity] = {}
    sum_dict: dict[str, TokenRarity] = {}
    ic_dict: dict[str, TokenRarity] = {}

    logger.debug("OpenRarity scoring")

    for token in tokens:
        token_identifier = token.token_identifier
        assert isinstance(token_identifier, EVMContractTokenIdentifier)
        token_id = str(token_identifier.token_id)

        try:
            token_features = TokenFeatureExtractor.extract_unique_attribute_count(
                token=token, collection=collection
            )

            harmonic_dict[token_id] = TokenRarity(
                token=token,
                token_features=token_features,
                score=harmonic_handler.score_token(collection=collection, token=token),
            )
            arthimetic_dict[token_id] = TokenRarity(
                token=token,
                token_features=token_features,
                score=arithmetic_handler.score_token(
                    collection=collection, token=token
                ),
            )
            geometric_dict[token_id] = TokenRarity(
                token=token,
                token_features=token_features,
                score=geometric_handler.score_token(collection=collection, token=token),
            )
            sum_dict[token_id] = TokenRarity(
                token=token,
                token_features=token_features,
                score=sum_handler.score_token(collection=collection, token=token),
            )
            ic_dict[token_id] = TokenRarity(
                token=token,
                token_features=token_features,
                score=ic_handler.score_token(collection=collection, token=token),
            )

        except Exception:
            logger.exception(f"Can't score token {token} with OpenRarity")

    # Calculate ranks of all assets given the scores
    arthimetic_ranked_tokens = extract_rank(arthimetic_dict)
    geometric_ranked_tokens = extract_rank(geometric_dict)
    harmonic_ranked_tokens = extract_rank(harmonic_dict)
    sum_ranked_tokens = extract_rank(sum_dict)
    ic_ranked_tokens = extract_rank(ic_dict)

    t1_stop = time()
    logger.debug(
        "OpenRarity scores resolution in seconds {seconds}".format(
            seconds=t1_stop - t1_start
        )
    )

    return OpenRarityScores(
        arithmetic_scores=arthimetic_ranked_tokens,
        geometric_scores=geometric_ranked_tokens,
        harmonic_scores=harmonic_ranked_tokens,
        sum_scores=sum_ranked_tokens,
        information_content_scores=ic_ranked_tokens,
    )


def _get_provider_rank(
    provider: RankProvider, token_with_rarity: TokenWithRarityData
) -> int | None:
    """Get rank for the particular provider

    Parameters
    ----------
    provider : RankProvider
        rank provider
    token : Token
        token
    """
    rarities = token_with_rarity.rarities
    rarity_datas = list(filter(lambda rarity: rarity.provider == provider, rarities))
    return rarity_datas[0].rank if len(rarity_datas) > 0 else None


def _rank_diff(rank1: int | None, rank2: int | None) -> int | None:
    """Function that computes the rank difference

    Parameters
    ----------
    rank1 : int | None
        rank of the asset
    rank2 : int | None
        rank of the asset

    Returns
    -------
    int | None
        absolute difference of ranks for the specific asset
    """
    if not rank1 or not rank2:
        return None

    return abs(rank1 - rank2)


def serialize_to_csv(
    collection_with_metadata: CollectionWithMetadata,
    tokens_with_rarity: list[TokenWithRarityData],
    dry_run: bool = False,
) -> list | None:
    """Serialize collection and ranking data to CSV

    Parameters
    ----------
    collection_with_metadata : Collection
    dry_run: bool
        If set to True, the CSV will not be written to disk but returned as an
        array of rows

    """
    slug = collection_with_metadata.opensea_slug
    testset = open(f"testset_{slug}.csv", "w")
    headers = [
        "slug",
        "token_id",
        "traits_sniper",
        "rarity_sniffer",
        "rarity_sniper",
        "arithmetic",
        "geometric",
        "harmonic",
        "sum",
        "information_content",
        "traits_sniper_rarity_sniffer_diff",
        "traits_sniper_rarity_sniper_diff",
        "traits_sniper_arithm_diff",
        "traits_sniper_geom_diff",
        "traits_sniper_harmo_diff",
        "traits_sniper_sum_diff",
        "traits_sniper_ic_diff",
        "rarity_sniffer_rarity_sniper_diff",
        "rarity_sniffer_arithm_diff",
        "rarity_sniffer_geom_diff",
        "rarity_sniffer_harmo_diff",
        "rarity_sniffer_sum_diff",
        "rarity_sniffer_ic_diff",
        "rarity_sniper_arithm_diff",
        "rarity_sniper_geom_diff",
        "rarity_sniper_harmo_diff",
        "rarity_sniper_sum_diff",
        "rarity_sniper_ic_diff",
    ]

    writer = csv.writer(testset)
    writer.writerow(headers)
    rows = []

    for token_with_rarity in tokens_with_rarity:
        traits_sniper_rank = _get_provider_rank(
            RankProvider.TRAITS_SNIPER, token_with_rarity
        )
        rarity_sniffer_rank = _get_provider_rank(
            RankProvider.RARITY_SNIFFER, token_with_rarity
        )
        rarity_sniper_rank = _get_provider_rank(
            RankProvider.RARITY_SNIPER, token_with_rarity
        )
        or_arithmetic_rank = _get_provider_rank(
            RankProvider.OR_ARITHMETIC, token_with_rarity
        )
        or_geometric_rank = _get_provider_rank(
            RankProvider.OR_GEOMETRIC, token_with_rarity
        )
        or_harmonic_rank = _get_provider_rank(
            RankProvider.OR_HARMONIC, token_with_rarity
        )
        or_sum_rank = _get_provider_rank(RankProvider.OR_SUM, token_with_rarity)
        or_ic_rank = _get_provider_rank(
            RankProvider.OR_INFORMATION_CONTENT, token_with_rarity
        )
        row = [
            slug,
            token_with_rarity.token.token_identifier.token_id,  # type: ignore
            traits_sniper_rank,
            rarity_sniffer_rank,
            rarity_sniper_rank,
            or_arithmetic_rank,
            or_geometric_rank,
            or_harmonic_rank,
            or_sum_rank,
            or_ic_rank,
            _rank_diff(traits_sniper_rank, rarity_sniffer_rank),
            _rank_diff(traits_sniper_rank, rarity_sniper_rank),
            _rank_diff(traits_sniper_rank, or_arithmetic_rank),
            _rank_diff(traits_sniper_rank, or_geometric_rank),
            _rank_diff(traits_sniper_rank, or_harmonic_rank),
            _rank_diff(traits_sniper_rank, or_sum_rank),
            _rank_diff(traits_sniper_rank, or_ic_rank),
            _rank_diff(rarity_sniffer_rank, rarity_sniper_rank),
            _rank_diff(rarity_sniffer_rank, or_arithmetic_rank),
            _rank_diff(rarity_sniffer_rank, or_geometric_rank),
            _rank_diff(rarity_sniffer_rank, or_harmonic_rank),
            _rank_diff(rarity_sniffer_rank, or_sum_rank),
            _rank_diff(rarity_sniffer_rank, or_ic_rank),
            _rank_diff(rarity_sniper_rank, or_arithmetic_rank),
            _rank_diff(rarity_sniper_rank, or_geometric_rank),
            _rank_diff(rarity_sniper_rank, or_harmonic_rank),
            _rank_diff(rarity_sniper_rank, or_sum_rank),
            _rank_diff(rarity_sniper_rank, or_ic_rank),
        ]
        if dry_run:
            rows.append(row)
        else:
            writer.writerow(row)

    return rows if rows else None


if __name__ == "__main__":
    """Script to resolve external datasets and compute rarity scores
    on test collections. Data resolved from opensea api

    Command to run:
    `python -m open_rarity.resolver.testset_resolver external`

        This will only produce ranks from OpenRarity and RaritySniffer by default.

    To run for all external providers:
    `TRAIT_SNIPER_API_KEY=<your key> python -m open_rarity.resolver.testset_resolver \
        external --trait_sniper --rarity_sniper`
    """
    args = parser.parse_args()
    logger = logging.getLogger("open_rarity_logger")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(strftime("testsetresolverlog_%H_%M_%m_%d_%Y.log"))
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)
    resolve_remote_rarity = args.resolve_external_rarity == "external"

    external_resolvers = []
    if args.fetch_trait_sniper:
        external_resolvers.append(RankProvider.TRAITS_SNIPER)
        if os.environ.get("TRAIT_SNIPER_API_KEY") is None:
            raise ValueError(
                "TRAIT_SNIPER_API_KEY not set. Required to fetch Traits Sniper data"
            )
    if args.fetch_rarity_sniffer:
        external_resolvers.append(RankProvider.RARITY_SNIFFER)
    if args.fetch_rarity_sniper:
        external_resolvers.append(RankProvider.RARITY_SNIPER)

    print(
        "Welcome to OpenRarity resolver! This is a tool to view OpenRarity rankings \n"
        "for given collection(s) and to compare them with existing ranking \n"
        "providers. If you just want to output OpenRarity rankings, you can use "
        "the script scripts/score_real_collections.py. \nFor full options, "
        "run `python3 -m open_rarity.resolver.testset_resolver --help`"
    )
    print(f"\nExecuting args: {args}")
    if resolve_remote_rarity:
        print(
            f"Fetching external ranks from: {[rp.value for rp in external_resolvers]}"
        )

    print(
        "\nNOTE: Resolving external data can take awhile due to external API rate"
        "\nlimits. Local caching will occur automatically so that future runs of "
        "\nthe same collection can be efficient. Expect a 10k collection to take >5 min"
        "\nwithout local cached data (timing based on exact external resolver(s) set). "
        "\nWith caching, expect ~15 seconds for processing."
    )

    resolve_collection_data(
        resolve_remote_rarity,
        external_rank_providers=external_resolvers,
        use_cache=args.cache_fetched_data,
        filename=args.filename,
    )
