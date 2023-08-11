import json
from pprint import pprint
import requests


# import faster_than_requests as requests


where_normal = {
				"_and": [
					{
						"_or": [
							{
								"submission_state": {
									"_eq": "open"
								}
							},
							{
								"submission_state": {
									"_eq": "api_only"
								}
							},
							{
								"external_program": {}
							}
						]
					},
					{
						"_not": {
							"external_program": {}
						}
					},
					{
						"_or": [
							{
								"_and": [
									{
										"state": {
											"_neq": "sandboxed"
										}
									},
									{
										"state": {
											"_neq": "soft_launched"
										}
									}
								]
							},
							{
								"external_program": {}
							}
						]
					}
				]
			}


where_offers_bounties = {
				"_and": [
					{
						"_or": [
							{
								"offers_bounties": {
									"_eq": True
								}
							},
							{
								"external_program": {
									"offers_rewards": {
										"_eq": True
									}
								}
							}
						]
					},
					{
						"_or": [
							{
								"submission_state": {
									"_eq": "open"
								}
							},
							{
								"submission_state": {
									"_eq": "api_only"
								}
							},
							{
								"external_program": {}
							}
						]
					},
					{
						"_not": {
							"external_program": {}
						}
					},
					{
						"_or": [
							{
								"_and": [
									{
										"state": {
											"_neq": "sandboxed"
										}
									},
									{
										"state": {
											"_neq": "soft_launched"
										}
									}
								]
							},
							{
								"external_program": {}
							}
						]
					}
				]
			}

def get_programs_raw(cursor):
	burp0_url = "https://hackerone.com/graphql"
	json_body = {
		"operationName": "DirectoryQuery",
		"variables": {
			"where": where_normal,
			"first": 100,
			"secureOrderBy": {
				"launched_at": {
					"_direction": "DESC"
				}
			},
			"product_area": "directory",
			"product_feature": "programs",
			"cursor": cursor
		},

		######################
		"query": """
			query DirectoryQuery($cursor: String, $secureOrderBy: FiltersTeamFilterOrder, $where: FiltersTeamFilterInput) {
			  me {
				id
				edit_unclaimed_profiles
				__typename
			  }
			  teams(first: 100, after: $cursor, secure_order_by: $secureOrderBy, where: $where) {
				pageInfo {
				  endCursor
				  hasNextPage
				  __typename
				}
				edges {
				  node {
					id
					bookmarked
					...TeamTableResolvedReports
					...TeamTableAvatarAndTitle
					...TeamTableLaunchDate
					...TeamTableMinimumBounty
					...TeamTableAverageBounty
					...BookmarkTeam
					__typename
				  }
				}
				__typename
			  }
			}
			
			fragment TeamTableResolvedReports on Team {
			  id
			  resolved_report_count
			  __typename
			}
			
			fragment TeamTableAvatarAndTitle on Team {
			  id
			  profile_picture(size: medium)
			  name
			  handle
			  submission_state
			  triage_active
			  publicly_visible_retesting
			  state
			  allows_bounty_splitting
			  external_program {
				id
				__typename
			  }
			  ...TeamLinkWithMiniProfile
			  __typename
			}
			
			fragment TeamLinkWithMiniProfile on Team {
			  id
			  handle
			  name
			  __typename
			}
			
			fragment TeamTableLaunchDate on Team {
			  id
			  launched_at
			  __typename
			}
			
			fragment TeamTableMinimumBounty on Team {
			  id
			  currency
			  base_bounty
			  __typename
			}
			
			fragment TeamTableAverageBounty on Team {
			  id
			  currency
			  average_bounty_lower_amount
			  average_bounty_upper_amount
			  __typename
			}
			
			fragment BookmarkTeam on Team {
			  id
			  bookmarked
			  __typename
			}
		"""
	}

	res = requests.post(burp0_url, json=json_body)
	j = res.json()
	return j


def get_programs(cursor):
	j = get_programs_raw(cursor)

	pageinfo = j["data"]["teams"]["pageInfo"]

	next_cursor, has_next_page = pageinfo["endCursor"], pageinfo["hasNextPage"]
	programs = [edge["node"] for edge in j["data"]["teams"]["edges"]]

	return has_next_page, next_cursor, programs


def get_programs_recursive(next_cursor, programs):
	global limit, verbose

	stop_criterium = len(programs) <= limit

	if stop_criterium is False:
		return programs

	# try:
	new_has_next_page, new_next_cursor, new_programs = get_programs(next_cursor)
	programs.extend(new_programs)
	# except Exception as e:
	#     stop_criterium = True

	if verbose: print(len(programs))

	if stop_criterium:
		return get_programs_recursive(new_next_cursor, programs)

	return programs


if __name__ == "__main__":
	limit = 5000
	verbose = True

	programs = get_programs_recursive("MjU", [])

	print("--")
	print(len(programs))

	with open("programs.json", "w") as f:
		json.dump(programs, f, indent=4, sort_keys=True)

	# handles = [program["handle"] for program in programs]
