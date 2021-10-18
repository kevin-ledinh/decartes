// server.js
console.log('May Node be with you')

const express = require('express');
const bodyParser= require('body-parser')
const MongoClient = require('mongodb').MongoClient
const app = express();

// Make sure you place body-parser before your CRUD handlers!
app.use(bodyParser.urlencoded({ extended: true }))

app.listen(3000, function() {
  console.log('listening on 3000')
})

// need to set view engine to ejs
app.set('view engine', 'ejs')

app.use(express.static('public'));

//Connect to database

MongoClient.connect("mongodb://localhost:27017/", { useUnifiedTopology: true })
  .then(client => {
    console.log('Connected to Database')
    const weaningFoodCol = client.db('ProductDb').collection('ProductCol')

    app.get('/', (req, res) => {
      res.sendFile(__dirname + '/index.html')
    })
    app.post('/search', (req, res) => {
      var searchStr = req.body.searchTerm;
      searchStr = searchStr.replace(/ /g, "\" \"")
      searchStr =  "\"".concat(searchStr,"\"")
      // console.log(searchStr)
      findQuery = {$text:{$search:searchStr}}

      if(req.body.excludeFlag == 'on') {
        findQuery = {$text:{$search:searchStr}, "store_name": { $ne : "Ocado"}}
      }

      weaningFoodCol.find(findQuery).toArray()
        .then(results => {
          // console.log(typeof req.body.isMobile)
          // console.log(req.body.excludeFlag)
          if (req.body.isMobile == 'true') {
            // console.log("use mobile site")
            res.render('index.ejs', { search: results })
          } else {
            // console.log("use full site")
            res.render('indexFull.ejs', { search: results })
          }
            
        })
        .catch(error => console.error(error))
      // ...
    })
  })
  .catch(console.error)



