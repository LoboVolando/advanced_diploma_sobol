import pytest
from loguru import logger

from app_tweets.schemas import TweetInSchema, TweetModelSchema
from schemas import SuccessSchema
from tests.test_media_service import create_many_medias


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_create_tweet(get_authors_id_list, author_service, tweet_db_service, faker):
    """тест записи твита в базу."""
    user_ids = await get_authors_id_list
    new_tweet = TweetInSchema(tweet_data=faker.text(100))
    for user_id in user_ids:
        attachments = await create_many_medias(count=2)
        # attachments = [attach. for attach in attachments]
        logger.warning(f"attachements: {attachments}")
        tweet = await tweet_db_service.create_tweet(new_tweet=new_tweet, author_id=user_id, attachments=attachments)
        logger.info(f"== {attachments == tweet.attachments}")
        assert isinstance(tweet, TweetModelSchema)
        assert tweet.id > 0
        assert tweet.content == new_tweet.tweet_data
        assert attachments == tweet.attachments
        assert set(tweet.dict().keys()) == {
            "id",
            "content",
            "author_id",
            "soft_delete",
            "likes",
            "attachments",
            "author",
        }


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_get_tweet_by_id(get_tweet_schemas_list, tweet_db_service):
    """тест получение твита по ид"""
    authors_list, tweet_list = await get_tweet_schemas_list
    assert len(authors_list) > 0
    assert len(tweet_list) > 0
    for tweet in tweet_list:
        selected_tweet = await tweet_db_service.get_tweet_by_id(tweet_id=tweet.id)
        assert isinstance(selected_tweet, TweetModelSchema)
        assert set(selected_tweet.dict().keys()) == {
            "id",
            "content",
            "author_id",
            "soft_delete",
            "likes",
            "attachments",
            "author",
        }
        assert selected_tweet == tweet


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_get_tweet_list_by_author_id(get_tweet_schemas_list, tweet_db_service):
    """тестируем получения списка твитов для автора"""
    authors_list, tweet_list = await get_tweet_schemas_list
    tweet_dict = {tweet.id: tweet for tweet in tweet_list}
    for author in authors_list:
        tweets = await tweet_db_service.get_list(author_id=author.id)
        assert len(tweets) > 0
        for tweet in tweets:
            assert isinstance(tweet, TweetModelSchema)
            assert set(tweet.dict().keys()) == {
                "id",
                "content",
                "author_id",
                "soft_delete",
                "likes",
                "attachments",
                "author",
            }
            assert tweet == tweet_dict.get(tweet.id)


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_update_likes_for_tweet(get_tweet_schemas_list, tweet_db_service, faker):
    """тест гбновления лайков"""
    authors_list, tweet_list = await get_tweet_schemas_list
    likes = [dict(user_id=author.id, name=author.name) for author in authors_list]
    assert len(likes) > 0
    for tweet in tweet_list:
        await tweet_db_service.update_like_in_tweet(tweet_id=tweet.id, likes=likes)
    for tweet in tweet_list:
        selected_tweet = await tweet_db_service.get_tweet_by_id(tweet_id=tweet.id)
        assert selected_tweet.likes == likes
    logger.info(f"verify likes in tweets")


@pytest.mark.dbtest
@pytest.mark.asyncio
async def test_delete_tweet(get_tweet_schemas_list, tweet_db_service):
    logger.info(f"delete tweets...")
    authors_list, tweet_list = await get_tweet_schemas_list
    for tweet in tweet_list:
        result = await tweet_db_service.delete_tweet(tweet_id=tweet.id, author_id=tweet.author_id)
        assert isinstance(result, SuccessSchema)
    for tweet in tweet_list:
        selected_tweet = await tweet_db_service.get_tweet_by_id(tweet_id=tweet.id)
        assert selected_tweet.id == tweet.id
        assert selected_tweet.soft_delete is True
    logger.info(f"delete tweets")
