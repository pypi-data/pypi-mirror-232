import logging
logging.basicConfig(level=logging.INFO)
from azuredevopsX.abstractdevops import AbstractDevOps
from azuredevopsX import factories
# Represents the teams in a project
class Team(AbstractDevOps):
	
	def __init__(self,personal_access_token, organization_url):
		super(Team,self).__init__(personal_access_token=personal_access_token,organization_url=organization_url)
	
	def get_teams(self, project_id):
		return self.core_client.get_teams(project_id)
	
	def get_teams_dict (self, project_id):
		result = self.core_client.get_teams(project_id = project_id)
		team_dict = {}
		
		for team in result:
			team_dict[team.name] = team.__dict__

		return team_dict;	

	def get_team (self, team_id, project_id):
		return self.core_client.get_team(team_id = team_id, project_id = project_id)
	
	def get_by_project_function(self, project_id,**kwargs):
		try:
			logging.info("Start function: get_all_team by project")
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			project = project_service.get_by_project(project_id)
			teams = []
			function = kwargs["function"]
			for team in self.get_teams(project_id = project.id):
				
				team.project = project.__dict__
				function (data=team, topic=kwargs["topic"], extra_data=kwargs["extra_data"])
				teams.append(team)
			
			return teams				

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 


	def get_by_project(self, project_id):
		try:
			logging.info("Start function: get_all_team by project")
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			project = project_service.get_by_project(project_id)
			teams = []
			for team in self.get_teams(project_id = project.id):
				team.additional_properties["project"] = project.__dict__
				teams.append(team)
			
			return teams				

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 

	
	def get_all(self, today = False):
		try:

			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			projects = project_service.get_all()
			teams = []
			for project in projects:
				for team in self.get_teams(project_id = project.id):
					team.additional_properties["project"] = project.__dict__
					teams.append(team)
			
			return teams				

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 
