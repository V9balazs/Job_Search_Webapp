import { useState } from 'react'

export default function App() {
   const [keywords, setKeywords] = useState('IT')
   const [location, setLocation] = useState('Budapest')
   const [jobs, setJobs] = useState([])
   const [loading, setLoading] = useState(false)

   async function handleSearch(e) {
      e.preventDefault()
      setLoading(true)
      try {
         const res = await fetch('http://localhost:8000/search', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ keywords, location, days: 7 })
         })
         const data = await res.json()
         setJobs(data.jobs || [])
      }
      catch (err) {
         console.error('Hiba a keresés során:', err)
      }
      setLoading(false)
   }

   return (
      <div style={{padding: 24, fontFamily: 'Arial'}}>
         Állás keresés
         <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <input
               value={keywords}
               onChange={e => setKeywords(e.target.value)}
               placeholder="Kulcsszavak (pl. IT, developer)"
               style={{ padding: 6, flex: 1 }}
            />
            <input
               value={location}
               onChange={e => setLocation(e.target.value)}
               placeholder="Helyszín (pl. Budapest)"
               style={{ padding: 6, flex: 1 }}
            />
            <button type="submit" style={{ padding: '6px 12px' }}>Keresés</button>
         </form>

         {loading && <p>Betöltés…</p>}

         <ul style={{ listStyle: 'none', padding: 0 }}>
            {jobs.map((job, idx) => (
               <li key={idx} style={{ margin: '12px 0', borderBottom: '1px solid #eee', paddingBottom: 8 }}>
               <a href={job.url} target="_blank" rel="noreferrer" style={{ fontWeight: 'bold', color: '#0070f3' }}>
                  {job.title}
               </a>
               <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                  {job.company} — {job.location} — {job.posted_date}
               </div>
               </li>
            ))}
         </ul>
      </div>
   )
}