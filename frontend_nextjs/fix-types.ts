import fs from 'fs';
import path from 'path';

const pagePath = path.join(__dirname, 'app', 'page.tsx');
let content = fs.readFileSync(pagePath, 'utf8');

// 1. Corrigir a interface GameResult
content = content.replace(
  /interface GameResult \{[\s\S]*?numbers: number\[\];[\s\S]*?sum: number;[\s\S]*?high_numbers: number;[\s\S]*?even_numbers: number;[\s\S]*?source: string;[\s\S]*?\}/,
  `interface GameResult {
  numbers: number[];
  sum: number;
  high_numbers: number;
  even_numbers: number;
  source: string;
  method?: string;
}`
);

// 2. Remover a propriedade 'method' do objeto demo se ainda existir
content = content.replace(
  /source: 'demo_mode',\s*\n\s*method: 'demo'/g,
  `source: 'demo_mode'`
);

fs.writeFileSync(pagePath, content, 'utf8');
console.log('✅ Arquivo page.tsx corrigido!');
