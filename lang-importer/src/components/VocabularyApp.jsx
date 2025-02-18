import React, { useState } from 'react';
import Groq from "groq-sdk";

// Define the schema for Marathi vocabulary word
const schema = {
  $defs: {
    WordPart: {
      properties: {
        nama: { title: "Nama", type: "string" },
        phonetic: { 
          items: { type: "string" },
          type: "array"
        }
      },
      required: ["nama", "phonetic"],
      title: "WordPart",
      type: "object"
    }
  },
  properties: {
    marathi: { title: "Marathi", type: "string" },
    phonetic: { title: "Phonetic", type: "string" },
    english: { title: "English", type: "string" },
    parts: {
      items: { $ref: "#/$defs/WordPart" },
      title: "Parts",
      type: "array"
    }
  },
  required: ["marathi", "phonetic", "english", "parts"],
  title: "MarathiWord",
  type: "object"
};


const VocabularyApp = () => {
  const [category, setCategory] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const getVocabulary = async (category) => {
    if (!import.meta.env.VITE_GROQ_API_KEY) {
      throw new Error('Groq API key is not configured. Please check your .env file.');
    }
    
    const groq = new Groq({
      apiKey: import.meta.env.VITE_GROQ_API_KEY,
      dangerouslyAllowBrowser: true  // Enable browser usage
    });
    
    console.log('Initializing Groq with API key present:', !!import.meta.env.VITE_GROQ_API_KEY);

    const jsonSchema = JSON.stringify(schema, null, 4);
    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: "system",
          content: `You are a Marathi vocabulary database that outputs words in JSON format.
          Generate an array of 10-15 words related to the given category.
          Each word must follow this schema: ${jsonSchema}`,
        },
        {
          role: "user",
          content: `Generate Marathi vocabulary words related to the category: ${category}`,
        },
      ],
      model: "mixtral-8x7b-32768",
      temperature: 0.3,
      stream: false,
      response_format: { type: "json_object" }
    });

    return completion.choices[0].message.content;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setCopied(false);

    try {
      console.log('Fetching vocabulary for category:', category);
      const response = await getVocabulary(category);
      console.log('API Response:', response);
      
      setResult(JSON.stringify(JSON.parse(response), null, 2));
    } catch (err) {
      console.error('Error details:', {
        message: err.message,
        stack: err.stack,
        category: category
      });
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(result);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div style={{ 
        backgroundColor: '#ffffff', 
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        padding: '20px'
      }}>
        <h1 style={{ marginBottom: '20px', color: '#333' }}>Marathi Vocabulary Generator</h1>
        
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Enter word category (e.g., colors, animals, emotions)"
              style={{
                flex: 1,
                padding: '8px 12px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                fontSize: '16px',
                color: '#333'
              }}
            />
            <button 
              type="submit" 
              disabled={loading || !category.trim()}
              style={{
                padding: '8px 16px',
                backgroundColor: loading ? '#cccccc' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Generating...' : 'Generate'}
            </button>
          </div>
        </form>

        {error && (
          <div style={{ 
            padding: '12px',
            backgroundColor: '#ffebee',
            color: '#c62828',
            borderRadius: '4px',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        {result && (
          <div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '10px'
            }}>
              <h3 style={{ margin: 0, color: '#333' }}>Generated Vocabulary</h3>
              <button
                onClick={handleCopy}
                style={{
                  padding: '6px 12px',
                  backgroundColor: copied ? '#4caf50' : '#007bff',
                  color: copied ? 'white' : 'white',
                  border: '1px solid #007bff',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                {copied ? 'Copied!' : 'Copy JSON'}
              </button>
            </div>
            <pre style={{ 
              backgroundColor: '#f0f0f0',
              padding: '15px',
              borderRadius: '4px',
              overflow: 'auto',
              maxHeight: '400px',
              border: '1px solid #ccc',
              color: '#333',
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              textAlign: 'left',
              fontFamily: 'monospace'
            }}>
              {result}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default VocabularyApp;