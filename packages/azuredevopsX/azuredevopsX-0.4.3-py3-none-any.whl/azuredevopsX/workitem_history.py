import logging
logging.basicConfig(level=logging.INFO)
from azuredevopsX.abstractdevops import AbstractDevOps
from azuredevopsX import factories

class WorkItemHistory(AbstractDevOps):

	def __init__(self,personal_access_token, organization_url):
		super(WorkItemHistory,self).__init__(personal_access_token=personal_access_token,organization_url=organization_url)
		self.serviceWorkitem = factories.WorkItemFactory(personal_access_token=personal_access_token,organization_url=organization_url)

	def get_by_project_function(self, project_id,**kwargs):
		try:
			logging.info("Start function: WorkItemHistory by project")
			function = kwargs["function"]
			work_items_list = self.serviceWorkitem.get_by_project(project_id)
			project_service = factories.ProjectFactory(personal_access_token=self.personal_access_token,organization_url=self.organization_url)
			
			revisions_list = []
			project = project_service.get_by_project(project_id)
			for work_item in work_items_list:
				revisions = self.work_item_tracking_client.get_revisions(project=work_item.fields['System.TeamProject'], id = work_item.id, expand="All")
				for revios in revisions:
					revios.project = project.__dict__
					function (data=revios, topic=kwargs["topic"], extra_data=kwargs["extra_data"])
				
				revisions_list.extend (revisions)

			logging.info("End function: WorkItemHistory by project")
			return revisions_list

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 	

	def get_by_project(self, project_id):
		try:
			logging.info("Start function: WorkItemHistory by project")
			
			work_items_list = self.serviceWorkitem.get_by_project(project_id)
			revisions_list = []
			
			for work_item in work_items_list:
				revisions = self.work_item_tracking_client.get_revisions(project=work_item.fields['System.TeamProject'], id = work_item.id, expand="All")
				revisions_list.extend (revisions)

			logging.info("End function: WorkItemHistory by project")
			return revisions_list

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 


	def get_all (self, today=False):
		try:
			logging.info("Start function: WorkItemHistory")
			
			work_items_list = self.serviceWorkitem.get_all(today=today)
			revisions_list = []
			
			for work_item in work_items_list:
				logging.info("Getting Revisisons: "+work_item.fields['System.TeamProject']+"--"+str(work_item.id))
				revisions = self.work_item_tracking_client.get_revisions(project=work_item.fields['System.TeamProject'], id = work_item.id, expand="All")
				revisions_list.extend (revisions)
				

			return revisions_list

		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 

	

	