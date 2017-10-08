// Imports the Google Cloud client library
const Language = require('@google-cloud/language');

// Instantiates a client
const language = Language();

// The text to analyze
const text = 'The people of the world will certainly be victorious';

const document = {
  'content': text,
  type: 'PLAIN_TEXT'
};

// Detects the sentiment of the text
language.analyzeEntitySentiment({ document: document })
  .then((results) => {
    const entities = results[0].entities;

    console.log(`Entities and sentiments:`);
    entities.forEach((entity) => {
      console.log(`  Name: ${entity.name}`);
      console.log(`  Type: ${entity.type}`);
      console.log(`  Score: ${entity.sentiment.score}`);
      console.log(`  Magnitude: ${entity.sentiment.magnitude}`);
    });
  })
  .catch((err) => {
    console.error('ERROR:', err);
  });
