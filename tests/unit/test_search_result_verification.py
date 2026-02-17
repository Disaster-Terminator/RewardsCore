"""
Tests for search result verification
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from search.search_engine import SearchEngine


class TestSearchResultVerification:
    """Test search result verification functionality"""

    @pytest.fixture
    def mock_config(self):
        """Create mock config"""
        config = MagicMock()
        config.get = MagicMock(
            side_effect=lambda key, default=None: {
                "anti_detection.human_behavior_level": "medium",
                "anti_detection.mouse_movement.micro_movement_probability": 0.3,
            }.get(key, default)
        )
        return config

    @pytest.fixture
    def mock_term_generator(self):
        """Create mock term generator"""
        generator = MagicMock()
        generator.get_random_term = MagicMock(return_value="test query")
        return generator

    @pytest.fixture
    def mock_anti_ban(self):
        """Create mock anti-ban module"""
        anti_ban = MagicMock()
        anti_ban.get_random_wait_time = MagicMock(return_value=5.0)
        return anti_ban

    @pytest.fixture
    def search_engine(self, mock_config, mock_term_generator, mock_anti_ban):
        """Create search engine with mocked dependencies"""
        return SearchEngine(
            config=mock_config,
            term_generator=mock_term_generator,
            anti_ban=mock_anti_ban,
        )

    @pytest.mark.asyncio
    async def test_verify_search_result_valid_url(self, search_engine):
        """Test verification with valid search URL"""
        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/search?q=test"
        mock_page.title = AsyncMock(return_value="test - Bing")
        mock_page.evaluate = AsyncMock(return_value=5)
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await search_engine._verify_search_result(mock_page, "test")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_search_result_invalid_url(self, search_engine):
        """Test verification with invalid URL"""
        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/"

        result = await search_engine._verify_search_result(mock_page, "test")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_search_result_with_results(self, search_engine):
        """Test verification with search results present"""
        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/search?q=test"
        mock_page.title = AsyncMock(return_value="test - Bing")
        mock_page.evaluate = AsyncMock(return_value=10)
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await search_engine._verify_search_result(mock_page, "test")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_search_result_no_results_indicator(self, search_engine):
        """Test verification with no results indicator"""
        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/search?q=test"
        mock_page.title = AsyncMock(return_value="test - Bing")
        mock_page.evaluate = AsyncMock(return_value=0)
        mock_page.query_selector = AsyncMock(return_value=AsyncMock())

        result = await search_engine._verify_search_result(mock_page, "test")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_search_result_title_contains_term(self, search_engine):
        """Test that search term appears in title"""
        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/search?q=python+tutorial"
        mock_page.title = AsyncMock(return_value="python tutorial - Bing")
        mock_page.evaluate = AsyncMock(return_value=5)
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await search_engine._verify_search_result(mock_page, "python tutorial")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_search_result_exception_handling(self, search_engine):
        """Test that exceptions are handled gracefully"""
        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/search?q=test"
        mock_page.title = AsyncMock(side_effect=Exception("Title error"))
        mock_page.evaluate = AsyncMock(return_value=5)

        result = await search_engine._verify_search_result(mock_page, "test")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_search_result_evaluate_error(self, search_engine):
        """Test handling of evaluate errors"""
        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/search?q=test"
        mock_page.title = AsyncMock(return_value="test - Bing")
        mock_page.evaluate = AsyncMock(side_effect=Exception("Evaluate error"))

        result = await search_engine._verify_search_result(mock_page, "test")
        assert result is True


class TestSearchResultVerificationIntegration:
    """Integration tests for search result verification"""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get = MagicMock(return_value="medium")
        return config

    @pytest.fixture
    def mock_term_generator(self):
        generator = MagicMock()
        generator.get_random_term = MagicMock(return_value="test")
        return generator

    @pytest.fixture
    def mock_anti_ban(self):
        anti_ban = MagicMock()
        anti_ban.get_random_wait_time = MagicMock(return_value=0.1)
        anti_ban.simulate_human_scroll = AsyncMock()
        return anti_ban

    @pytest.mark.asyncio
    async def test_verification_called_after_search(
        self, mock_config, mock_term_generator, mock_anti_ban
    ):
        """Test that verification is called after search submission"""
        engine = SearchEngine(
            config=mock_config,
            term_generator=mock_term_generator,
            anti_ban=mock_anti_ban,
        )

        mock_page = AsyncMock()
        mock_page.url = "https://www.bing.com/search?q=test"
        mock_page.title = AsyncMock(return_value="test - Bing")
        mock_page.evaluate = AsyncMock(return_value=5)
        mock_page.query_selector = AsyncMock(return_value=None)

        result = await engine._verify_search_result(mock_page, "test")
        assert result is True


class TestAntiBanRandomization:
    """Test anti-ban randomization improvements"""

    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get = MagicMock(
            side_effect=lambda key, default=None: {
                "search.wait_interval.min": 5,
                "search.wait_interval.max": 15,
            }.get(key, default)
        )
        return config

    def test_random_wait_time_distribution(self, mock_config):
        """Test that random wait time follows expected distribution"""
        from browser.anti_ban_module import AntiBanModule

        anti_ban = AntiBanModule(mock_config)

        times = [anti_ban.get_random_wait_time() for _ in range(100)]

        assert all(5 <= t <= 18 for t in times)

        mean = sum(times) / len(times)
        assert 8 <= mean <= 12

    def test_random_wait_time_within_bounds(self, mock_config):
        """Test that random wait time is within bounds"""
        from browser.anti_ban_module import AntiBanModule

        anti_ban = AntiBanModule(mock_config)

        for _ in range(50):
            wait_time = anti_ban.get_random_wait_time()
            assert wait_time >= 5
            assert wait_time <= 18
