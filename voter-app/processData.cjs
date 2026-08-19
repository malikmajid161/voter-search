const fs = require('fs');
const path = require('path');

const inputPath = path.join(__dirname, '../ALL_VOTERS_COMBINED_FINAL.json');
const votersOutputPath = path.join(__dirname, 'public/voter_data_final.json');
const familiesOutputPath = path.join(__dirname, 'public/family_data.json');

console.log('Reading input data...');
const rawData = fs.readFileSync(inputPath, 'utf8');
const voters = JSON.parse(rawData);

console.log(`Processing ${voters.length} voters...`);

const families = {};

voters.forEach(voter => {
    // Some logic to group: Use BlockCode + GharanaNo + FatherNameUrdu
    // But typically GharanaNo within a block is the family.
    // Let's use BlockCode + "_" + GharanaNo
    const blockCode = voter.BlockCode || 'UNKNOWN_BLOCK';
    const gharanaNo = voter.GharanaNo || 'UNKNOWN_GHARANA';
    
    // As per user's prompt: "like people having same father name GharanaNo"
    // Let's use GharanaNo and FatherNameUrdu to be safe, or just GharanaNo.
    // Let's use BlockCode + GharanaNo
    const familyId = `${blockCode}_${gharanaNo}`;
    
    voter.FamilyId = familyId;
    
    if (!families[familyId]) {
        families[familyId] = {
            id: familyId,
            blockCode: blockCode,
            gharanaNo: gharanaNo,
            members: []
        };
    }
    
    families[familyId].members.push(voter);
});

console.log(`Created ${Object.keys(families).length} families.`);

// Save voters with FamilyId
fs.writeFileSync(votersOutputPath, JSON.stringify(voters, null, 2));
console.log('Saved voter_data_final.json');

// Save families
fs.writeFileSync(familiesOutputPath, JSON.stringify(families, null, 2));
console.log('Saved family_data.json');
