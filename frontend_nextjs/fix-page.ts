import fs from 'fs';
import path from 'path';

const filePath = path.join(__dirname, 'app', 'page.tsx');
let content = fs.readFileSync(filePath, 'utf8');

// A variável 'day' já é um number (useState com new Date().getDate())
// Mas o input onChange retorna string, então precisamos converter
// Encontre a linha do fetch e corrija
content = content.replace(
  /body: JSON\.stringify\(\{ day: parseInt\(day\) \}\),/,
  'body: JSON.stringify({ day: Number(day) }),'
);

// Ou melhor, adicione uma verificação
content = content.replace(
  /const generateWithAI = async \(\) => {[\s\S]*?body: JSON\.stringify[^}]+},/,
  `const generateWithAI = async () => {
    setLoading(true);
    setError('');
    setGame(null);

    try {
      const response = await fetch('http://localhost:8080/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day: Number(day) }),
      });`
);

fs.writeFileSync(filePath, content, 'utf8');
console.log('Arquivo page.tsx corrigido!');
