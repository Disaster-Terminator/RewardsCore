import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class GraphQLClient:
    """GitHub GraphQL 客户端 - 获取完整评论（避免截断）"""

    def __init__(self, token: str):
        self.token = token
        self.endpoint = "https://api.github.com/graphql"
        self.rest_endpoint = "https://api.github.com"
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        执行 GraphQL 查询

        Args:
            query: GraphQL 查询语句
            variables: 查询变量

        Returns:
            查询结果数据

        Raises:
            Exception: GraphQL 错误
        """
        if variables is None:
            variables = {}

        response = httpx.post(
            self.endpoint,
            json={"query": query, "variables": variables},
            headers=self.headers,
            timeout=30.0,
        )

        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            raise Exception(f"GraphQL Error: {data['errors']}")

        return data["data"]

    def fetch_pr_threads(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """
        获取 PR 的评论线程 (包含 Thread ID)

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            pr_number: PR 编号

        Returns:
            线程列表，每个线程包含 id (Thread ID)、isResolved、path、line 等
        """
        query = """
        query($owner: String!, $repo: String!, $pr: Int!) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              reviewThreads(last: 50) {
                nodes {
                  id
                  isResolved
                  path
                  line
                  comments(first: 1) {
                    nodes {
                      author { login }
                      body
                      url
                    }
                  }
                }
              }
            }
          }
        }
        """

        data = self._execute(query, {"owner": owner, "repo": repo, "pr": pr_number})

        threads = data["repository"]["pullRequest"]["reviewThreads"]["nodes"]

        if len(threads) >= 50:
            logger.warning("Review Thread 数量达到上限 (50)，可能存在分页截断！")

        return threads

    def fetch_pr_reviews(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """
        获取 PR 的 Review 级别评论（总览意见）

        Sourcery 的总览意见在 reviews API 中，包含：
        - "high level feedback"（无法单独解决）
        - "Prompt for AI Agents"

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            pr_number: PR 编号

        Returns:
            Review 列表，每个包含 id、body、author 等
        """
        query = """
        query($owner: String!, $repo: String!, $pr: Int!) {
          repository(owner: $owner, name: $repo) {
            pullRequest(number: $pr) {
              reviews(last: 20) {
                nodes {
                  id
                  body
                  state
                  author { login }
                  url
                  submittedAt
                }
              }
            }
          }
        }
        """

        data = self._execute(query, {"owner": owner, "repo": repo, "pr": pr_number})

        reviews = data["repository"]["pullRequest"]["reviews"]["nodes"]

        return reviews

    def resolve_thread(self, thread_id: str) -> bool:
        """
        解决线程 (Mutation)

        Args:
            thread_id: Thread 的 GraphQL Node ID

        Returns:
            True 如果解决成功

        Raises:
            Exception: API 调用失败
        """
        mutation = """
        mutation($threadId: ID!) {
          resolveReviewThread(input: {threadId: $threadId}) {
            thread {
              isResolved
            }
          }
        }
        """

        try:
            data = self._execute(mutation, {"threadId": thread_id})
            is_resolved = data["resolveReviewThread"]["thread"]["isResolved"]
            logger.info(f"Thread {thread_id} resolved: {is_resolved}")
            return is_resolved
        except Exception as e:
            logger.error(f"Failed to resolve thread {thread_id}: {e}")
            raise

    def reply_to_thread(self, thread_id: str, body: str) -> str:
        """
        在线程下回复 (Mutation)

        Args:
            thread_id: Thread 的 GraphQL Node ID
            body: 回复内容

        Returns:
            新评论的 ID

        Raises:
            Exception: API 调用失败
        """
        mutation = """
        mutation($threadId: ID!, $body: String!) {
          addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
            comment {
              id
            }
          }
        }
        """

        try:
            data = self._execute(mutation, {"threadId": thread_id, "body": body})
            comment_id = data["addPullRequestReviewThreadReply"]["comment"]["id"]
            logger.info(f"Reply posted to thread {thread_id}, comment ID: {comment_id}")
            return comment_id
        except Exception as e:
            logger.error(f"Failed to reply to thread {thread_id}: {e}")
            raise

    def fetch_issue_comments(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """
        获取 PR 的 Issue Comments（REST API）

        Qodo 的 PR Reviewer Guide 存储在 Issue Comments 中，而非 Review Threads。
        Issue Comments 是 PR 页面上的普通评论。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            pr_number: PR 编号

        Returns:
            Issue Comment 列表，每个包含 id、body、user、created_at 等
        """
        url = f"{self.rest_endpoint}/repos/{owner}/{repo}/issues/{pr_number}/comments"

        all_comments = []
        page = 1

        while True:
            response = httpx.get(
                url, headers=self.headers, params={"page": page, "per_page": 100}, timeout=30.0
            )

            response.raise_for_status()
            comments = response.json()

            if not comments:
                break

            all_comments.extend(comments)
            page += 1

            if len(comments) < 100:
                break

        logger.info(f"Fetched {len(all_comments)} issue comments for PR #{pr_number}")
        return all_comments
