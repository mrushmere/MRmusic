"""
Routes and views for the flask application.
"""
from __future__ import print_function
import sys

from datetime import datetime
from flask import Flask, url_for, render_template
from mrmusic import app
from forms import BestAlbumForm, AlbumReviewForm
import config
import pydocumentdb.document_client as document_client


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/create')
def create():
    """Renders the contact page."""
    client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})

    # Attempt to delete the database.  This allows this to be used to recreate as well as create
    try:
        db = next((data for data in client.ReadDatabases() if data['id'] == config.DOCUMENTDB_DATABASE))
        client.DeleteDatabase(db['_self'])
    except:
        pass

    # Create database
    db = client.CreateDatabase({ 'id': config.DOCUMENTDB_DATABASE })
    print(db, file=sys.stderr)

    # Create collection
    collection = client.CreateCollection(db['_self'],{ 'id': config.DOCUMENTDB_COLLECTION }, { 'offerType': 'S1' })

    # Create document
    document = client.CreateDocument(collection['_self'],
        { 'id': config.DOCUMENTDB_DOCUMENT,
          'The Life of Pablo': 0,
          'Blackstar': 0,
          'Emily\'s D+Evolution': 0,
          'name': config.DOCUMENTDB_DOCUMENT 
        })

    return render_template(
       'create.html',
        title='Create Page',
        year=datetime.now().year,
        message='You just created a new database, collection, and document.  Your old votes have been deleted')

@app.route('/createreviews')
def createreviews():
    """Renders the contact page."""
    client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})

    # Attempt to delete the database.  This allows this to be used to recreate as well as create
    try:
        db = next((data for data in client.ReadDatabases() if data['id'] == config.DOCUMENTDB_REVIEWDATABASE))
        client.DeleteDatabase(db['_self'])
    except:
        pass

    # Create database
    db = client.CreateDatabase({ 'id': config.DOCUMENTDB_REVIEWDATABASE })
    print(db, file=sys.stderr)
    # Create collection
    collection = client.CreateCollection(db['_self'],{ 'id': config.DOCUMENTDB_REVIEWCOLLECTION }, { 'offerType': 'S1' })

    return render_template(
       'createreviews.html',
        title='Create Reviews Page',
        year=datetime.now().year,
        message='You just created a new database and collection for reviews!, all old reviews have been deleted')



@app.route('/vote', methods=['GET', 'POST'])
def vote(): 
    form = BestAlbumForm()
    replaced_document ={}
    if form.validate_on_submit(): # is user submitted vote
        print('It works!', file=sys.stderr)  
        client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})

        # Read databases and take first since id should not be duplicated.
        # db = next((data for data in client.ReadDatabases() if data['id'] == config.DOCUMENTDB_DATABASE))
        databases = list(client.ReadDatabases())
        for database in databases:
            if database['id'] == config.DOCUMENTDB_DATABASE:
                db = database
        print(db, file=sys.stderr)
        # Read collections and take first since id should not be duplicated.
        coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == config.DOCUMENTDB_COLLECTION))

        # Read documents and take first since id should not be duplicated.
        doc = next((doc for doc in client.ReadDocuments(coll['_self']) if doc['id'] == config.DOCUMENTDB_DOCUMENT))

        # Take the data from the deploy_preference and increment our database
        doc[form.deploy_preference.data] = doc[form.deploy_preference.data] + 1
        replaced_document = client.ReplaceDocument(doc['_self'], doc)

        # Create a model to pass to results.html
        class VoteObject:
            choices = dict()
            total_votes = 0

        vote_object = VoteObject()
        vote_object.choices = {
            "The Life of Pablo" : doc['The Life of Pablo'],
            "Blackstar" : doc['Blackstar'],
            "Emily's D+Evolution" : doc['Emily\'s D+Evolution']
        }
        vote_object.total_votes = sum(vote_object.choices.values())

        return render_template(
            'results.html', 
            year=datetime.now().year, 
            vote_object = vote_object)

    else :
        return render_template(
            'vote.html', 
            title = 'Vote',
            year=datetime.now().year,
            form = form)

@app.route('/submitalbum', methods=['GET', 'POST'])
def submitalbum():
    form = AlbumReviewForm()
    if form.validate_on_submit():
        client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})
        print('client connected', file=sys.stderr)
        # Read databases and get the review one
        databases = list(client.ReadDatabases())
        for database in databases:
            if database['id'] == config.DOCUMENTDB_REVIEWDATABASE:
                db = database
        print(db, file=sys.stderr)
        print('It works!', file=sys.stderr)
        # Read collections 
        #coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == config.DOCUMENTDB_REVIEWCOLLECTION))
        collections = client.ReadCollections()
        for col in collections:
            if col['id'] == config.DOCUMENTDB_REVIEWCOLLECTION:
                coll = col

        # Create document
        document = client.CreateDocument(coll['_self'],
            { 'id': config.DOCUMENTDB_REVIEWDOCUMENT,
              'Album': 'testing',
              'Artist': 'testing',
              'Release': 'testing',
              'name': config.DOCUMENTDB_REVIEWDOCUMENT 
            })


        # Create a model to pass to albums.html
        class AlbumObject:
            albuminfo = dict()

        album_object = AlbumObject()
        album_object.albuminfo = {
            "Album": document['Album'],
            "Artist": document['Artist'],
            "Release": document['Release']
        }
        return render_template(
            'viewalbums.html',
            album_object = album_object)
    else:
        return render_template(
            'submitalbum.html', 
            form = form)






