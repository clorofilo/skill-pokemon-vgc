const { calculate, Generations, Pokemon, Move, Field } = require('@smogon/calc');

const gen = Generations.get(9);

function parseEvs(evs = {}) {
  return {
    hp: evs.hp ?? 0,
    atk: evs.atk ?? 0,
    def: evs.def ?? 0,
    spa: evs.spa ?? 0,
    spd: evs.spd ?? 0,
    spe: evs.spe ?? 0,
  };
}

function parseBoosts(boosts = {}) {
  return {
    atk: boosts.atk ?? 0,
    def: boosts.def ?? 0,
    spa: boosts.spa ?? 0,
    spd: boosts.spd ?? 0,
    spe: boosts.spe ?? 0,
  };
}

try {
  const input = JSON.parse(process.argv[2]);

  const attacker = new Pokemon(gen, input.attacker.species, {
    item: input.attacker.item,
    nature: input.attacker.nature,
    evs: parseEvs(input.attacker.evs),
    boosts: parseBoosts(input.attacker.boosts),
    teraType: input.attacker.teraType,
    isTera: !!input.attacker.teraType,
  });

  const defender = new Pokemon(gen, input.defender.species, {
    item: input.defender.item,
    nature: input.defender.nature,
    evs: parseEvs(input.defender.evs),
    boosts: parseBoosts(input.defender.boosts),
    teraType: input.defender.teraType,
    isTera: !!input.defender.teraType,
  });

  const move = new Move(gen, input.move);

  const field = new Field({
    weather: input.field?.weather,
    terrain: input.field?.terrain,
    gameType: 'Doubles',
  });

  const result = calculate(gen, attacker, defender, move, field);
  const range = result.range();
  const hp = defender.originalCurHP;
  const ko = result.kochance();

  console.log(JSON.stringify({
    description: result.fullDesc(),
    damage: [...result.damage],
    min: range[0],
    max: range[1],
    minPercent: ((range[0] / hp) * 100).toFixed(1),
    maxPercent: ((range[1] / hp) * 100).toFixed(1),
    koChance: ko.d !== undefined ? ko.n + '/' + ko.d : ko.n + '/1',
    koText: ko.text,
  }));
} catch (err) {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
}
