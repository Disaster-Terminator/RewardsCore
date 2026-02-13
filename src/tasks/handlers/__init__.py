"""
Task Handlers for different Microsoft Rewards task types
"""

from tasks.handlers.url_reward_task import UrlRewardTask
from tasks.handlers.quiz_task import QuizTask
from tasks.handlers.poll_task import PollTask

__all__ = [
    'UrlRewardTask',
    'QuizTask',
    'PollTask',
]
