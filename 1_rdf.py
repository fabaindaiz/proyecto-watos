import json
import pandas as pd #for handling csv and csv contents
from rdflib import Graph, Literal, RDF, URIRef, Namespace #basic RDF handling
from rdflib.namespace import FOAF , XSD #most common namespaces
import urllib.parse #for parsing strings to URI's

MAX_ROWS = 1000

# Utils
def clean(name: str) -> str:
    return urllib.parse.quote(name)


print('Reading CSV...')
df = pd.read_csv('datasets/job_descriptions.csv', sep=',', quotechar='"', encoding='utf-8')
lenght = len(df.index)

graph = Graph()
EX = Namespace('http://ex.org/')
schema = Namespace('http://schema.org/')

uri_job = Namespace('http://ex.org/job/')
uri_qualification = Namespace('http://ex.org/qualification/')
uri_worktype = Namespace('http://ex.org/worktype/')
uri_country = Namespace('http://ex.org/country/')
uri_location = Namespace('http://ex.org/location/')
uri_company = Namespace('http://ex.org/company/')
uri_sector = Namespace('http://ex.org/sector/')
uri_industry = Namespace('http://ex.org/industry/')
uri_jobportal = Namespace('http://ex.org/jobportal/')
uri_preference = Namespace('http://ex.org/preference/')

print('Creating RDF...')
for index, row in df.iterrows():
    job_id = URIRef(uri_job + str(row['Job Id']))

    # Job
    graph.add((job_id, RDF.type, EX.Job))
    graph.add((job_id, schema.title, Literal(row['Job Title'], datatype=XSD.string)))
    graph.add((job_id, schema.role, Literal(row['Role'], datatype=XSD.string)))
    graph.add((job_id, schema.date, Literal(row['Job Posting Date'], datatype=XSD.date)))

    # Experience
    experience = row['Experience'].replace(' Years', '').split(' to ')
    graph.add((job_id, schema.minExperience, Literal(experience[0], datatype=XSD.integer)))
    graph.add((job_id, schema.maxExperience, Literal(experience[1], datatype=XSD.integer)))

    # Salary
    salary = row['Salary Range'].replace('$', '').replace('K', '000').split('-')
    graph.add((job_id, schema.minSalary, Literal(salary[0], datatype=XSD.integer)))
    graph.add((job_id, schema.maxSalary, Literal(salary[1], datatype=XSD.integer)))

    # Qualification
    node_qualification = URIRef(uri_qualification + clean(row['Qualifications']))
    if (node_qualification, None, None) not in graph:
        graph.add((node_qualification, RDF.type, EX.Qualification))
        graph.add((node_qualification, schema.name, Literal(row['Qualifications'], datatype=XSD.string)))
    
    graph.add((job_id, schema.qualification, node_qualification))

    # Work Type
    node_worktype = URIRef(uri_worktype + clean(row['Work Type']))
    if (node_worktype, None, None) not in graph:
        graph.add((node_worktype, RDF.type, EX.WorkType))
        graph.add((node_worktype, schema.name, Literal(row['Work Type'], datatype=XSD.string)))
    
    graph.add((job_id, schema.workType, node_worktype))

    # Country
    node_country = URIRef(uri_country + clean(row['Country']))
    if (node_country, None, None) not in graph:
        graph.add((node_country, RDF.type, EX.Country))
        graph.add((node_country, schema.name, Literal(row['Country'], datatype=XSD.string)))
        graph.add((node_country, schema.latitude, Literal(row['latitude'], datatype=XSD.float)))
        graph.add((node_country, schema.longitude, Literal(row['longitude'], datatype=XSD.float)))
    
    graph.add((job_id, schema.country, node_country))

    # Location
    node_location = URIRef(uri_location + clean(row['location']))
    if (node_location, None, None) not in graph:
        graph.add((node_location, RDF.type, EX.Location))
        graph.add((node_location, schema.name, Literal(row['location'], datatype=XSD.string)))
        graph.add((node_country, schema.hasLocation, node_location))
    
    graph.add((job_id, schema.location, node_location))

    # Company
    node_company = URIRef(uri_company + clean(row['Company']))
    if (node_company, None, None) not in graph:
        graph.add((node_company, RDF.type, EX.Company))
        graph.add((node_company, schema.name, Literal(row['Company'], datatype=XSD.string)))
        graph.add((node_company, schema.size, Literal(row['Company Size'], datatype=XSD.integer)))

        try:
            profile = json.loads(row['Company Profile'])
            graph.add((node_company, schema.website, Literal(profile['Website'], datatype=XSD.string)))

            # Sector
            node_sector = URIRef(uri_sector + clean(profile['Sector']))
            if (node_sector, None, None) not in graph:
                graph.add((node_sector, RDF.type, EX.Sector))
                graph.add((node_sector, schema.name, Literal(profile['Sector'], datatype=XSD.string)))
            
            graph.add((node_company, schema.sector, node_sector))

            # Industry
            node_industry = URIRef(uri_industry + clean(profile['Industry']))
            if (node_industry, None, None) not in graph:
                graph.add((node_industry, RDF.type, EX.Industry))
                graph.add((node_industry, schema.name, Literal(profile['Industry'], datatype=XSD.string)))
            
            graph.add((node_company, schema.industry, node_industry))
        
        except:
            print(f"Error in company profile ( {index} : {row['Company Profile']} )")

    graph.add((job_id, schema.company, node_company))

    node_jobportal = URIRef(uri_jobportal + clean(row['Job Portal']))
    if (node_jobportal, None, None) not in graph:
        graph.add((node_jobportal, RDF.type, EX.JobPortal))
        graph.add((node_jobportal, schema.name, Literal(row['Job Portal'], datatype=XSD.string)))
    
    graph.add((job_id, schema.jobPortal, node_jobportal))
    
    # Preference
    preference = URIRef(uri_preference + clean(row['Preference']))
    if (preference, None, None) not in graph:
        graph.add((preference, RDF.type, EX.Preference))
        graph.add((preference, schema.name, Literal(row['Preference'], datatype=XSD.string)))

    graph.add((job_id, schema.preference, preference))

    if index == MAX_ROWS:
        break

#print(g.serialize(format='turtle'))

graph.serialize('graphs/result.ttl',format='turtle')
print('Done!')
