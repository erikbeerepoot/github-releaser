from prettytable import PrettyTable
import requests 
import argparse


parser = argparse.ArgumentParser(description='Github release API tool')
parser.add_argument('--tag', dest='tag', required=True, help='Tag you want to create/delete/modify')
parser.add_argument('--description', dest='description', required=False, help='Tag description')
parser.add_argument('--prerelease', dest='preRelease', required=False, help='Is this release a pre-release?')
parser.add_argument('--release-name', dest='releaseName', required=False, help='The name of this release/tag')
parser.add_argument('--organization', dest='organization', required=True, help='URL of repository on which to create release')
parser.add_argument('--base-url', dest='baseURL', required=False, default="https://api.github.com", help='URL of repository on which to create release')
parser.add_argument('--repo-name', dest='repoName', required=False, help='URL of repository on which to create release')
parser.add_argument('--api-token', dest='APIToken', required=True, help='Github API token')


def check_request_status(request,expectedStatus,errorMessage):
		if(request.status_code!=expectedStatus):
			print('Github API Request failed with message: %s' % errorMessage)
			return False;
		return True;

class User:
	def __init__(self,APIToken):
		self.APIToken = APIToken;

class Organization:
	def __init__(self,user,login,URL,avatarURL='',description='',organizationID=-1):
		self.authHeader = {'Authorization' : 'token ' + user.APIToken};

		self.login = login
		self.id = organizationID
		self.URL = URL;
		self.avatarURL = avatarURL;
		self.description = description;
	
	def list_releases(self,repo):
		endpoint = self.URL + '/repos/%s/%s/releases' % (self.login,repo);

		req = requests.get(endpoint,headers=self.authHeader);

		if(check_request_status(req,200,"Could not get releases.")==False):
			return []

		releases = [];
		for release in req.json():
			rel = Release(release["name"],release["tag_name"],release["body"],release["prerelease"],release["name"],repo,release['id'])
			releases.append(rel);		
		return releases;

	@staticmethod
	def print_releases(releases):
		
		t = PrettyTable(['Release name:', 'Tag:', 'ID:'])
		for release in releases:
			t.add_row([release.name, release.tag, release.id])
		print t



class Release:
	def __init__(self,name,tag='',description='',prerelease='',releaseName='',repo='', releaseID=-1):
		self.name = name;
		self.tag = tag;
		self.body = description;
		self.prerelease = prerelease;
	 	self.releaseName = releaseName;
	 	self.id = releaseID;

class GithubRelease:
	def __init__(self,user):		

		self.authHeader = {'Authorization' : 'token ' + user.APIToken};
	
	

	def get_release(self,release,endpoint='/releases/tags/'):
		endpoint =  release.repo + endpoint + release.tag
		req = requests.get(endpoint,headers=self.authHeader);		

		if(self.check_request_status(req,200,"Release not found.")):
			release.id = req.json()['id']			
		return release;

	


	def create_release(self,endpoint='/releases'):
		payload = { "tag_name": release.tag, 
					"name" : release.name,
					"target_commitsh": release.tag, 
					"body": release.body,
					"prerelease" : release.prerelease }		
		
		endpoint = release.repo + endpoint;
		req = requests.post(endpoint,json=payload,headers=self.authHeader);		
		return req;

	def update_release(self,release,endpoint='/releases'):
		#Get release ID
		result = self.get_release();
		releaseID = -1;

		

		payload = { "tag_name": release.tag, 
					"name" : release.name,
					"target_commitsh": release.tag, 
					"body": release.body,
					"prerelease" : release.prerelease }		
		
		endpoint = release.repo + endpoint;
		req = requests.patch(endpoint,json=payload,headers=self.authHeader);	

	def delete_release(self,release,endpoint='/releases/'):
		#Get release ID
		result = self.get_release();
		releaseID = -1;

		if(result==200):
			releaseID =  result.json()['id'];
		else:
			print('Trying to delete non-existent release!')
			return;

		#Delete 
		endpoint = self.repo + endpoint + str(releaseID);
		req = requests.delete(endpoint,headers=self.authHeader);		

		if(result==204):
			print('Succesfully delete release');

		return req;		

	def upload_asset(self,release,fileToUpload,endpoint='/assets'):
		
		#Get release ID
		result = self.get_release();
		
		uploadURL = "";
		print(result)
		if(result.status_code!=200):
			print('Trying to upload asset for non-existent release!')
			return;

		#
		uploadURL = result.json()['upload_url'];		
		uploadURL = uploadURL.replace('{?name}','?name=extension.zip',1);
		print(uploadURL)
		print(fileToUpload)

		contentHeader = {'Content-Type' : 'application/octet-stream'};
		payload = { "name": fileToUpload } 
		data = open(fileToUpload, 'rb').read()		
		req = requests.post(uploadURL,json=payload,data=data,headers=dict(self.authHeader.items()+contentHeader.items()));		
		print(req.text)
		
		
		

if __name__ == "__main__":
	args = parser.parse_args()
	
	#Need this everyone
	user = User(args.APIToken);	

	#List releases
	organization = Organization(user,args.organization,args.baseURL);
	releases = organization.list_releases(args.repoName);
	Organization.print_releases(releases);

	#release = Release(name=args.tag,tag=args.tag,description=args.description,releaseName=args.releaseName,repo=args.repoName);
	
	#
	#githubReleaser = GithubReleaser(args.APIToken)
	#release = githubReleaser.get_release(release);
	#githubReleaser.list_releases(mediacoreargs.repoURL);
	#print(release.id)


	#mediacoreRepo 	= 'https://api.github.com/repos/mediacore/';
	#GithubAPIToken 	= '3affdf06f82d3743c9fc3af4d984b64ee2dfeee6';

	