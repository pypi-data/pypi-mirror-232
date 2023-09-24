import logging
logging.basicConfig(level=logging.INFO)
from azuredevopsX import factories
from azuredevopsX.abstractdevops import AbstractDevOps

# Represent the time-box in a project 
class Interaction(AbstractDevOps):
	def __init__(self,personal_access_token, organization_url):
		super(Interaction,self).__init__(personal_access_token=personal_access_token,organization_url=organization_url)
		

	def get_interactions(self, project, team):
		try:
			logging.info("Start function: get_work_items")
			team_context = self.create_team_context(project, team)
			logging.info("End function: get_work_items")
			return self.work_client.get_team_iterations(team_context)
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__)
	
	
	def get_by_project_function(self, project_id,**kwargs):

		try:
			logging.info("Start function: get_all_interaction by project")
			interactions = []
			
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			team_service = factories.TeamFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			project = project_service.get_by_project(project_id)
			
			function = kwargs["function"]

			teams = team_service.get_teams(project.id)
			for team in teams:
				team_context = self.create_team_context(project, team)
				for interaction in self.work_client.get_team_iterations(team_context):
						
					interaction.project = project.__dict__
					interaction.team = team.__dict__
					interaction.attributes = interaction.attributes.__dict__

					function (data=interaction, topic=kwargs["topic"], extra_data=kwargs["extra_data"])
					
					interactions.append (interaction)
			
			logging.info("End function: get_all_interaction by project")
			return interactions
			
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__)
	
	def get_by_project_dict(self, project_id):
		
		interactions = self.get_by_project(project_id=project_id)
		interactions_dict = {}

		for interaction in interactions:
			interactions_dict[interaction.path] = interaction.__dict__
		
		return interactions_dict

	def get_by_project(self,project_id):

		try:
			logging.info("Start function: get_all_interaction by project")
			interactions = []
			
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			team_service = factories.TeamFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			project = project_service.get_by_project(project_id)
			
			teams = team_service.get_teams(project.id)
			for team in teams:
				team_context = self.create_team_context(project, team)
				for interaction in self.work_client.get_team_iterations(team_context):
						
					interaction.additional_properties["project"] = project.__dict__
					interaction.additional_properties["team"] = team.__dict__
					interaction.attributes = interaction.attributes.__dict__
					interactions.append (interaction)
			
			logging.info("End function: get_all_interaction by project")
			return interactions
			
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__)
	

	def get_all(self, today = False):

		try:
			logging.info("Start function: get_all_interaction")
			interactions = []
			
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			team_service = factories.TeamFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			projects = project_service.get_all()
			
			for project in projects:
				teams = team_service.get_teams(project.id)
				for team in teams:
					team_context = self.create_team_context(project, team)
					for interaction in self.work_client.get_team_iterations(team_context):
						
						interaction.additional_properties["project"] = project.__dict__
						interaction.additional_properties["team"] = team.__dict__
						interaction.attributes = interaction.attributes.__dict__
						interactions.append (interaction)
			
			logging.info("End function: get_all_interaction")
			return interactions
			
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__)
	
	