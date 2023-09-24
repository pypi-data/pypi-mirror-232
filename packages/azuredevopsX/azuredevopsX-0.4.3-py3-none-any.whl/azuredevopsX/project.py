import logging
logging.basicConfig(level=logging.INFO)
from azuredevopsX.abstractdevops import AbstractDevOps

# Represents a software Project
class Project(AbstractDevOps):
	def __init__(self,personal_access_token, organization_url):
		super(Project,self).__init__(
					personal_access_token=personal_access_token,
			       organization_url=organization_url
				   )
		# Returns a list of project
	
	def get_all_function(self, today=False, **kwargs): 
		
		projects = []
		try:
			logging.info("Start function: get_projects")
			function = kwargs["function"]
			get_projects_response = self.core_client.get_projects()
				
			for project in get_projects_response:
				projects.append(project)
				if function is not None:
					function (data=project, topic=kwargs["topic"], extra_data=kwargs["extra_data"])
				
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 

		logging.info("Retrieve All Projects")
		return projects

	
	def get_by_project(self, project_id):
		try:
			logging.info("Start function: get one project")
			
			return self.core_client.get_project(project_id)
				
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 
		
	
	def get_all(self, today=False): 
		projects = []
		try:
			logging.info("Start function: get_projects")
			
			get_projects_response = self.core_client.get_projects()
				
			for project in get_projects_response:
				projects.append(project)
		
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 

		logging.info("Retrieve All Projects")
		return projects

	def get_processes(self):
		return self.work_item_process_tracking_client.get_list_of_processes()

	def get_process_behaviors(self, process_id):
		return self.work_item_process_tracking_client.get_process_behaviors(process_id)
    
	def get_process_by_its_id(self, process_type_id):
		return self.work_item_process_tracking_client.get_process_by_its_id(process_type_id)
    
	def get_state_definitions(self, process_id):
		return self.work_item_process_tracking_client.get_state_definitions(process_id)