from flask import current_app

from tests.base import BaseTestCase

import unittest


class GroupTestCase(BaseTestCase):
    def test_basic_operation(self):
        self.login()
        # Create Group
        data = self.OK(self.post("/v1/group", json=dict(title="GROUP")))
        group_id = data["items"][0]["id"]
        data = self.OK(self.get("/v1/group", query_string=dict(group=group_id)))
        self.assertEqual(data["items"][0]["title"], "GROUP")

        # Create Action
        data = self.OK(
            self.post("/v1/group/action", json=dict(title="ACTION0", group=group_id))
        )
        action_id = data["items"][0]["id"]
        data = self.OK(
            self.get("/v1/group/action", query_string=dict(action=action_id))
        )
        self.assertEqual(data["items"][0]["title"], "ACTION0")
        self.assertEqual(data["items"][0]["finished"], 0)

        # Finish Action
        data = self.OK(
            self.put("/v1/group/action", json=dict(action=action_id, finished=1))
        )
        self.assertEqual(data["items"][0]["finished"], 1)

    def test_recursive_actions(self):
        """
        a0     a0
        |       |___
        a1 ->  a1   a2
        |
        a2
        """
        self.login()
        data = self.OK(self.post("/v1/group", json=dict(title="GROUP")))
        group_id = data["items"][0]["id"]

        # Create Action 0
        data = self.OK(
            self.post("/v1/group/action", json=dict(title="ACTION0", group=group_id))
        )
        action0_id = data["items"][0]["id"]

        # Create Action 1
        data = self.OK(
            self.post(
                "/v1/group/action",
                json=dict(title="ACTION1", group=group_id, aggs=[action0_id]),
            )
        )
        action1_id = data["items"][0]["id"]

        # Create Action 2
        data = self.OK(
            self.post(
                "/v1/group/action",
                json=dict(title="ACTION2", group=group_id, aggs=[action1_id]),
            )
        )
        action2_id = data["items"][0]["id"]

        data = self.OK(
            self.get(
                "/v1/group/actions",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.assertEqual(len(data["items"]), 3)

        data = self.OK(
            self.get(
                "/v1/group/action/aggregate",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.assertEqual(len(data["items"]), 2)

        for item in data["items"]:
            self.assertEqual(item["descendant_id"], item["ancestor_id"] + 1)

        data = self.OK(
            self.put(
                "/v1/group/action", json=dict(action=action2_id, aggs=[action0_id])
            )
        )
        data = self.OK(
            self.get(
                "/v1/group/action/aggregate",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.assertEqual(len(data["items"]), 2)

        for item in data["items"]:
            self.assertEqual(item["ancestor_id"], action0_id)

    def test_depend_actions(self):
        """
        a0     a0
        |       |___
        a1 ->  a1   a2
        |
        a2
        """
        self.login()
        data = self.OK(self.post("/v1/group", json=dict(title="GROUP")))
        group_id = data["items"][0]["id"]

        # Create Action 0
        data = self.OK(
            self.post("/v1/group/action", json=dict(title="ACTION0", group=group_id))
        )
        action0_id = data["items"][0]["id"]

        # Create Action 1
        data = self.OK(
            self.post(
                "/v1/group/action",
                json=dict(title="ACTION1", group=group_id, deps=[action0_id]),
            )
        )
        action1_id = data["items"][0]["id"]

        # Create Action 2
        data = self.OK(
            self.post(
                "/v1/group/action",
                json=dict(title="ACTION2", group=group_id, deps=[action1_id]),
            )
        )
        action2_id = data["items"][0]["id"]

        data = self.OK(
            self.get(
                "/v1/group/actions",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.assertEqual(len(data["items"]), 3)

        data = self.OK(
            self.get(
                "/v1/group/action/depend",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.format(data)
        self.assertEqual(len(data["items"]), 2)

        for item in data["items"]:
            self.assertEqual(item["descendant_id"], item["ancestor_id"] + 1)

        data = self.OK(
            self.put(
                "/v1/group/action", json=dict(action=action2_id, deps=[action0_id])
            )
        )
        data = self.OK(
            self.get(
                "/v1/group/action/depend",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.format(data)
        self.assertEqual(len(data["items"]), 2)

        for item in data["items"]:
            self.assertEqual(item["ancestor_id"], action0_id)

    @unittest.expectedFailure
    def test_failed_actions(self):
        self.login()
        data = self.OK(self.post("/v1/group", json=dict(title="GROUP")))
        group_id = data["items"][0]["id"]

        # Create Action 0
        data = self.OK(
            self.post("/v1/group/action", json=dict(title="ACTION0", group=group_id))
        )
        action0_id = data["items"][0]["id"]

        # Create Action 1 OK
        data = self.OK(
            self.post(
                "/v1/group/action",
                json=dict(
                    title="ACTION1", group=group_id, aggs=[action0_id, action0_id]
                ),
            )
        )
        action1_id = data["items"][0]["id"]

        # Create Action 2 ERR
        data = self.ERR(
            self.post(
                "/v1/group/action",
                json=dict(
                    title="ACTION2", group=group_id, aggs=[action0_id, action1_id]
                ),
            )
        )
        action2_id = data["items"][0]["id"]

    def test_attribute_cluster(self):
        self.login()
        # Create Group
        data = self.OK(self.post("/v1/group", json=dict(title="GROUP")))
        group_id = data["items"][0]["id"]

        # Create Group Cluster
        data = self.OK(
            self.post(
                "/v1/group/cluster",
                json=dict(group=group_id, title="CLUSTER", type="text"),
            )
        )
        cluster_id = data["items"][0]["id"]

        # Create Action
        data = self.OK(
            self.post("/v1/group/action", json=dict(title="ACTION", group=group_id))
        )
        action_id = data["items"][0]["id"]

        # Add Attribute
        data = self.OK(
            self.post(
                "/v1/group/attr",
                json=dict(cluster=cluster_id, type="text", text="ATTR"),
            )
        )
        attr_id = data["items"][0]["id"]

        # Get AttributeClusters
        data = self.OK(
            self.get("/v1/group/clusters", query_string=dict(group=group_id))
        )
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(len(data["items"][0]["attrs"]), 1)
        self.assertEqual(data["items"][0]["attrs"][0]["type"], "text")
        self.assertEqual(data["items"][0]["attrs"][0]["text"], "ATTR")

        # Add Attribute to Action
        data = self.OK(
            self.post(
                "/v1/group/action/belong", json=dict(action=action_id, attr=attr_id)
            )
        )

        # Modify Attribute
        data = self.OK(
            self.put(
                "/v1/group/attr",
                json=dict(attr=attr_id, type="text", text="ATTR1"),
            )
        )

        # Get Actions
        data = self.OK(
            self.get(
                "/v1/group/actions",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(len(data["items"][0]["attrs"]), 1)
        self.assertEqual(data["items"][0]["attrs"][0]["id"], attr_id)
        self.assertEqual(data["items"][0]["attrs"][0]["text"], 'ATTR1')

        # Remove Attribute from Action
        data = self.OK(
            self.delete(
                "/v1/group/action/belong",
                query_string=dict(action=action_id, attr=attr_id),
            )
        )

        # Get Actions
        data = self.OK(
            self.get(
                "/v1/group/actions",
                query_string=dict(group=group_id, offset=1, limit=10),
            )
        )
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(len(data["items"][0]["attrs"]), 0)


    def test_user_group(self):
        self.login()
        data = self.OK(self.get("/v1/group/user"))
