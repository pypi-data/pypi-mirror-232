import logging
logging.basicConfig(level=logging.INFO)
from azuredevopsX.abstractdevops import AbstractDevOps
from azuredevopsX import factories

# Represents a Backlog of project and Team
class Backlog(AbstractDevOps):

	def __init__(self,personal_access_token, organization_url):
		super(Backlog,self).__init__(personal_access_token=personal_access_token,organization_url=organization_url)
	
		
	# Return a backlog from a project and team
	def get_backlog(self,project,team): 
		try:
			logging.info("Start function: get_backlog")
			team_context = self.create_team_context(project, team)
			logging.info("End function: get_backlog")
			return self.work_client.get_backlogs(team_context)
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 
	
	def get_by_project_function(self, project_id,**kwargs):
		try:
			logging.info("Start function: get_backlog by project")
			
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			team_service = factories.TeamFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			project = project_service.get_by_project(project_id)
			backlogs = []
			teams = team_service.get_teams(project.id)
			
			function = kwargs["function"]

			for team in teams:
				team_context = self.create_team_context(project, team)		
				
				
				backlogs_team = self.work_client.get_backlogs(team_context)
				for backlog in backlogs_team:
					backlog = backlog.__dict__
					backlog["project"] = project.__dict__
					backlog["team"] = team.__dict__
					column_fields = []
					for column_field in backlog["column_fields"]:
						column_fields.append (column_field.__dict__)
					
					backlog["column_fields"] = column_fields
					
					
					function (data=backlog, topic=kwargs["topic"], extra_data=kwargs["extra_data"])

					backlogs.append(backlog)
					logging.info("End function: get_backlog")
			return backlogs	

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 
	
	def get_by_project(self, project_id):
		try:
			logging.info("Start function: get_backlog by project")
			
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			team_service = factories.TeamFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			project = project_service.get_by_project(project_id)
			backlogs = []
			teams = team_service.get_teams(project.id)
			for team in teams:
				team_context = self.create_team_context(project, team)		
				logging.info("End function: get_backlog")
				backlogs.extend (self.work_client.get_backlogs(team_context))
			
			return backlogs	

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 
	
	def get_all(self,today = False):
		try:
			logging.info("Start function: get_backlog")
			
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			team_service = factories.TeamFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			projects = project_service.get_all()
			backlogs = []
			for project in projects:
				teams = team_service.get_teams(project.id)
				for team in teams:
					team_context = self.create_team_context(project, team)		
					logging.info("End function: get_backlog")
					backlogs.extend (self.work_client.get_backlogs(team_context))
			
			return backlogs
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__)

	