import os
from wasabi import msg  # type: ignore[import]

from prompt.ingestion.util import setup_client

from dotenv import load_dotenv

load_dotenv()


def init_schema(model: str = "gpt-3.5-turbo"):
    msg.divider("Creating Document and Chunk class")

    client = setup_client()

    chunk_schema = {
        "classes": [
            {
                "class": "Chunk",
                "description": "Chunks of Documentations",
                "vectorizer": "text2vec-openai",
                "moduleConfig": {
                    "generative-openai": {"model": model}
                },  # gpt-4 / gpt-3.5-turbo
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        "name": "doc_uuid",
                        "dataType": ["text"],
                        "description": "Document UUID",
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True,
                                "vectorizePropertyName": False,
                            }
                        },
                    },
                    {
                        "name": "chunk_id",
                        "dataType": ["number"],
                        "description": "Document chunk from the whole document",
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True,
                                "vectorizePropertyName": False,
                            }
                        },
                    },
                ],
            }
        ]
    }

    document_schema = {
        "classes": [
            {
                "class": "Document_test",
                "description": "Documentation",
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        "name": "doc_link",
                        "dataType": ["text"],
                        "description": "Link to document",
                    },
                ],
            }
        ]
    }

    if client.schema.exists("Document_test"):
        user_input = input(
            "Document_test class already exists, do you want to overwrite it? (y/n): "
        )
        if user_input.strip().lower() == "y":
            client.schema.delete_class("Document_test")
            client.schema.delete_class("Chunk")
            client.schema.create(document_schema)
            client.schema.create(chunk_schema)
            msg.good("'Document_test' and 'Chunk' schemas created")
        else:
            msg.warn("Skipped deleting Document and Chunk schema, nothing changed")
    else:
        client.schema.create(document_schema)
        client.schema.create(chunk_schema)
        msg.good("'Document_test' and 'Chunk' schemas created")

    if client._connection.embedded_db:
        msg.info("Stopping Weaviate Embedded")
        client._connection.embedded_db.stop()
    msg.info("Done")

#---------------------------------------main class-------------------------------------------------------


# def init_schema_main(model: str="gpt-3.5-turbo"):
#     msg.divider("Creating Document and Other classes")
#     client = setup_client()

#     #--------------------------Document Schema--------------------------
#     document_schema = {
#         "classes": [
#             {            
#                 "class": "Document", # name of the class
#                 # a description of what this class represents
#                 "description": "A document class to store documents of different format and origin",             
#                 # class properties
#                 "properties": [                  
#                     # document identifier name/title
#                     {
#                         "name": "title",
#                         "dataType": ["text"],
#                         "description": "The title of the document", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": False,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },
#                     # document content 
#                     {
#                         "name": "content",
#                         "dataType": ["text"],
#                         "description": "The entire content of the document",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": False,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },
#                     # content word count              
#                     {
#                         "name": "wordCount",
#                         "dataType": ["int"],
#                         "description": "The word count of the content",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },                  
#                     # document reference Id
#                     {
#                         "name": "uid",
#                         "dataType": ["text"],
#                         "description": "The url or id of the original document",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },  
#                     # document location
#                     {
#                         "name": "url",
#                         "dataType": ["text"],
#                         "description": "what type of id is the resource Id: url, google_drive, etc.",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     }, 
#                     # document metadata
#                     {
#                         "name": "metadata",
#                         "dataType": ["text"],
#                         "description": "necessary metadata in the form of text",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     }, 
#                     # relation with transformed item 
#                     {
#                         "name": "tdocument",
#                         "dataType": ["TDocument"],
#                         "description": "relation with transformed output"                  
#                     },                                                
#                     # relation with tags 
#                     {
#                         "name": "tags",
#                         "dataType": ["DocumentTag"],
#                         "description": "The category of the document in, what, who, what, why dimensions"               
#                     },
#                 ],
#                 "moduleConfig": {"generative-openai": {"model": model}},
#                 "vectorizer": "text2vec-openai",
#             }, 
#         ]
#     }
#     #--------------------------Transformed Document Schema-------------------------
#     t_document_schema = {
#         "classes": [
#             {
#                 "class": "TDocument", # name of the class
#                 # a description of what this class represents
#                 "description": "A class to store all types of transformation outputs",             
#                 "properties": [ # class properties 
#                     # reference to document
#                     {
#                         "name": "document",
#                         "dataType": ["Document"],
#                         "description": "Reference to document"                   
#                     }, 
#                     # the output of the transformer function                           
#                     {
#                         "name": "content",
#                         "dataType": ["text"],
#                         "description": "The summary content", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": False,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },
#                     # content word count
#                     {
#                         "name": "wordCount",
#                         "dataType": ["int"],
#                         "description": "The word count of the content",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },                  
#                     # the output of the transformer function                           
#                     {
#                         "name": "metadata",
#                         "dataType": ["TMetadata"],
#                         "description": "The transformer metadata"                   
#                     },                
#                 ],
#                 "moduleConfig": {"generative-openai": {"model": model}},
#                 "vectorizer": "text2vec-openai",
#             },
#         ]
#     }
#     #--------------------------Document Tag Schema------------------------
#     document_tag_schema = {
#         "classes": [
#             {
#                 "class": "DocumentTag", # name of the class
#                 # a description of what this class represents
#                 "description": "A document category class",             
#                 "properties": [ # class properties   
#                     # reference to document
#                     {
#                         "name": "document",
#                         "dataType": ["Document"],
#                         "description": "Reference to document"                   
#                     },   
#                     # document schema version              
#                     {
#                         "name": "version",
#                         "dataType": ["int"],
#                         "description": "The version of the metadata",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },                                                         
#                     # describes what type of document it is e.g. report, slide, code, etc.
#                     {
#                         "name": "type",
#                         "dataType": ["text"],
#                         "description": "The type of the document", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },
#                     # describes the format of the original document e.g. pdf, txt, image, etc.
#                     {
#                         "name": "format",
#                         "dataType": ["text"],
#                         "description": "The format of the document", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },                
#                     # describes the origin - what caused the document
#                     {
#                         "name": "source",
#                         "dataType": ["text"],
#                         "description": "the conceptual or physical source of the document", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },   
#                     # describes the simple actions we will apply on this document  
#                     {
#                         "name": "action",
#                         "dataType": ["text"],
#                         "description": "The follow up action required", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     }, 
#                     # describes its value type as project, eskai, monitoring, etc. 
#                     {
#                         "name": "valueType",
#                         "dataType": ["text[]"],
#                         "description": "The value chain category this document belongs", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },
#                     # describes the value name in valueType category
#                     {
#                         "name": "value",
#                         "dataType": ["text[]"],
#                         "description": "The values this document provides to its downstream use cases", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },
#                     },
#                 ],
#                 "moduleConfig": {"generative-openai": {"model": model}},
#                 "vectorizer": "text2vec-openai",  
#             },
#         ]
#     }
#     #--------------------------Transformed Metadata Schema-------------------------
#     t_meta_schema = {
#         "classes": [
#             {        
#                 "class": "TMetadata", 
#                 # a description of what this class represents
#                 "description": "A class to store metadata of transformation outputs",             
#                 "properties": [ # class properties  
#                     # reference to trasnformed document
#                     {
#                         "name": "tdocument",
#                         "dataType": ["TDocument"],
#                         "description": "Reference to transformed document"                  
#                     },                   
#                     # the transformed schema version
#                     {
#                         "name": "version",
#                         "dataType": ["int"],
#                         "description": "The version of the document",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },
#                     },                            
#                     # the content of the transformer function e.g. code path, prompt, etc. 
#                     {
#                         "name": "function",
#                         "dataType": ["text"],
#                         "description": "The content of the transformer", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },
#                     # function content word count              
#                     {
#                         "name": "wordCount",
#                         "dataType": ["int"],
#                         "description": "The word count of the function content",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     },                  
#                     # the record name of the transformer function
#                     {
#                         "name": "name",
#                         "dataType": ["text"],
#                         "description": "The identifier name of the method used to produce the summary", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },
#                     },
#                     # the category of the transformer function e.g. prompt, ai_function, python_function, etc.
#                     {
#                         "name": "category",
#                         "dataType": ["text"],
#                         "description": "The function category used to produce the summary", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                 
#                     },
#                     # the parameters of the transformer function
#                     {
#                         "name": "params",
#                         "dataType": ["text"],
#                         "description": "The parameters used to produce the summary", 
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": True,
#                             }
#                         },                    
#                     }, 
#                 ],
#                 "moduleConfig": {"generative-openai": {"model": model}},
#                 "vectorizer": "text2vec-openai",
#             }
#         ]
#     }
#     #--------------------------Segment Schema------------------------
#     #TODO: Replacement for the transformed doc
#     segment_schema = {
#         "classes": [
#             {
#                 "class": "Segment",
#                 "description": "Segment of Documentations",
#                 "properties": [
#                     {
#                         "name": "text",
#                         "dataType": ["text"],
#                         "description": "Content of the document",
#                     },
#                     {
#                         "name": "doc_name",
#                         "dataType": ["text"],
#                         "description": "Document name",
#                     },
#                     {
#                         "name": "doc_type",
#                         "dataType": ["text"],
#                         "description": "Document type",
#                     },
#                     {
#                         "name": "doc_uuid",
#                         "dataType": ["text"],
#                         "description": "Document UUID",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": False,
#                             }
#                         },
#                     },
#                     {
#                         "name": "chunk_id",
#                         "dataType": ["number"],
#                         "description": "Document chunk from the whole document",
#                         "moduleConfig": {
#                             "text2vec-openai": {
#                                 "skip": True,
#                                 "vectorizePropertyName": False,
#                             }
#                         },
#                     },
#                 ],
#                 "vectorizer": "text2vec-openai",
#                 "moduleConfig": {"generative-openai": {"model": model}},
#             }
#         ]
#     }
#     #---------------------------Other Doc Schema---------------------------
#     #TODO: Should be merged into the main document schema
#     o_doc_schema = {
#         "classes": [
#             {
#                 "class": "O_Doc",
#                 "description": "Documentation",
#                 "properties": [
#                     {
#                         "name": "text",
#                         "dataType": ["text"],
#                         "description": "Content of the document",
#                     },
#                     {
#                         "name": "doc_name",
#                         "dataType": ["text"],
#                         "description": "Document name",
#                     },
#                     {
#                         "name": "doc_type",
#                         "dataType": ["text"],
#                         "description": "Document type",
#                     },
#                     {
#                         "name": "doc_link",
#                         "dataType": ["text"],
#                         "description": "Link to document",
#                     },
#                 ],
#             }
#         ]
#     }

#     if client.schema.exists("O_Doc"):
#         user_input = input(
#             "Warning: Document class already exists, do you want to overwrite it? (y/n): ")
#         if user_input.strip().lower() == "y":
#             user_input0 = input(
#                 "Warning: All existing data will be deleted! Are you sure? (y/n): ")
#             if user_input0.strip().lower() == "y":
#                 client.schema.delete_class("Document")
#                 #client.schema.delete_class("TDocument")
#                 client.schema.delete_class("DocumentTag")
#                 client.schema.delete_class("TMetadata")
#                 client.schema.delete_class("Segment") # used as t_doc
#                 client.schema.delete_class("O_Doc")
            
#                 client.schema.create(document_schema)
#                 #client.schema.create(t_document_schema)
#                 client.schema.create(document_tag_schema)
#                 client.schema.create(t_meta_schema)
#                 client.schema.create(segment_schema)
#                 client.schema.create(o_doc_schema)
                
#                 msg.good("'Document' and 'Other' schemas created")
#         else:
#             msg.warn("Skipped deleting Document and Chunk schema, nothing changed")
#     else:
#         client.schema.create(document_schema)
#         client.schema.create(t_document_schema)
#         client.schema.create(document_tag_schema)
#         client.schema.create(t_meta_schema)
#         client.schema.create(segment_schema)
#         client.schema.create(o_doc_schema)
    
#         msg.good("'Document' and 'Other' schemas created")

#     if client._connection.embedded_db:
#         msg.info("Stopping Weaviate Embedded")
#         client._connection.embedded_db.stop()
#     msg.info("Done")


