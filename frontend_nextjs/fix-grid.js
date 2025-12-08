const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'app', 'bolao', 'page.tsx');

fs.readFile(filePath, 'utf8', (err, data) => {
  if (err) {
    console.error('Erro ao ler arquivo:', err);
    return;
  }
  
  // Padrões a serem corrigidos
  const patterns = [
    // Padrão: <Grid item xs={...} md={...}>
    { regex: /<Grid item xs=(\{[^}]+}) md=(\{[^}]+})>/g, replace: '<Grid xs=$1 md=$2>' },
    { regex: /<Grid item xs=(\{[^}]+}) sm=(\{[^}]+})>/g, replace: '<Grid xs=$1 sm=$2>' },
    { regex: /<Grid item xs=(\{[^}]+}) lg=(\{[^}]+})>/g, replace: '<Grid xs=$1 lg=$2>' },
    { regex: /<Grid item xs=(\{[^}]+}) xl=(\{[^}]+})>/g, replace: '<Grid xs=$1 xl=$2>' },
    
    // Padrão: <Grid item xs={...}>
    { regex: /<Grid item xs=(\{[^}]+})>/g, replace: '<Grid xs=$1>' },
    { regex: /<Grid item md=(\{[^}]+})>/g, replace: '<Grid md=$1>' },
    { regex: /<Grid item sm=(\{[^}]+})>/g, replace: '<Grid sm=$1>' },
    { regex: /<Grid item lg=(\{[^}]+})>/g, replace: '<Grid lg=$1>' },
    { regex: /<Grid item xl=(\{[^}]+})>/g, replace: '<Grid xl=$1>' },
    
    // Padrão: <Grid item>
    { regex: /<Grid item>/g, replace: '<Grid>' },
    
    // Padrão: <Grid item { ... outras props }
    { regex: /<Grid item (?!xs=|md=|sm=|lg=|xl=)(\w+=)/g, replace: '<Grid $1' },
  ];

  let fixedData = data;
  
  patterns.forEach(pattern => {
    fixedData = fixedData.replace(pattern.regex, pattern.replace);
  });

  // Contar quantas foram corrigidas
  const beforeCount = (data.match(/Grid item/g) || []).length;
  const afterCount = (fixedData.match(/Grid item/g) || []).length;
  
  fs.writeFile(filePath, fixedData, 'utf8', (err) => {
    if (err) {
      console.error('Erro ao salvar arquivo:', err);
      return;
    }
    console.log(`Corrigidas ${beforeCount - afterCount} instâncias de 'Grid item'`);
    console.log(`Restantes: ${afterCount}`);
    console.log('Arquivo corrigido com sucesso!');
    
    if (afterCount > 0) {
      console.log('\nInstâncias restantes:');
      const lines = fixedData.split('\n');
      lines.forEach((line, index) => {
        if (line.includes('Grid item')) {
          console.log(`Linha ${index + 1}: ${line.trim()}`);
        }
      });
    }
  });
});
