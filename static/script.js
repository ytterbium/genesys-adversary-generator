const data = JSON.parse(json_data);


function click_row(id){ 
  element = document.getElementById(id);
  if (element.type == 'radio')
    element.checked = true
  else
    element.checked = (element.checked) ? false : true;
  update()
};

function update(){
  choices = [];

  // find all checked elements
  var inputs = document.querySelectorAll('table input')
  for (var i=0, n=inputs.length, input; i < n; i++){
    input = inputs[i];
    if (input.checked) 
      choices.push(data[input.name][input.value]);
  }
  

  // Condensation of all inputs
  result = {"power_level": {"combat": 0, "social": 0, "general": 0},
    "defense": {"strain_threshold": 0, "wound_threshold": 0, "soak": 0, "melee_defense": 0, "ranged_defense": 0},
    "skills": {},
    "talents" : [],
    "abilities": [],
    "caracteristics": {"brawn": 0, "agility": 0, "intellect": 0, "cunning": 0, "willpower": 0, "presence": 0},
  };

  for (var i = 0, n = choices.length; i < n; i++)
    for (var item in choices[i]){
      values = choices[i][item];

      if (item == 'caracs'){
        result['caracteristics'] = values 
        result['defense']['soak'] += values['brawn']

      } else if (item == 'power_level')
        for (var name in values)
          result["power_level"][name] += values[name];

      else if (item == 'skills')
        for (var name in values){
          prev = (name in result["skills"]) ? result["skills"][name] : 0;
          result["skills"][name] = Math.max(prev, values[name]);
        }

      else if (item == 'talent')
        result["talents"].push(values + ' <span class="desc">(' + choices[i]['desc'] + ')</span>')

      else if (item == 'ability')
        result["abilities"].push(values + ' <span class="desc">(' + choices[i]['desc'] + ')</span>')

      else if (item == 'weapons')
        result["weapons"] = values

      else if (item == 'equipment')
        result["equipment"] = values
        
      else if (item == "defense"){
        for (var name in values)
          result["defense"][name.replace(' ', '_')] += values[name];
        
      }; 
    };
  
  adversary_type = document.querySelector('input[name=type]:checked').value;
  if (adversary_type == 'minion'){
    if (result.caracteristics.brawn == 1)
      result.defense["wound_threshold"] += 3
    else result.defense["wound_threshold"] += 5
  } 
  else if (adversary_type == 'rival')
    result.defense["wound_threshold"] += 8 + result.caracteristics.brawn
  else {
    result.defense["wound_threshold"] += 12 + result.caracteristics.brawn;
    result.defense.strain_threshold += 10 + result.caracteristics.willpower;
  }
  
    
    // Affichage

  var st = document.querySelector('.st')
  if (nemesis.checked)
    st.style.display = 'unset'
  else
    st.style.display = 'none';
  
    
  var caracs = result['caracteristics'];
  var text;
  for (var id in caracs){
    text = document.querySelector('.nb.' + id);
    text.textContent = caracs[id]; 
  };

  var level = result['power_level'];
  
  for (var id in level){
    text = document.querySelector('.nb.' + id);
    text.textContent = level[id]; 
  };
  
  text = document.querySelector('.skills');
    var skill_array = [];
    var skills = result['skills'];
    for (name in skills)
      skill_array.push(name + ' ' + skills[name]);
    text.textContent = skill_array.sort().join(', ') + '.';
    if (Object.values(skills).length == 0) 
      text.textContent = 'None.';

  text = document.querySelector('.talents');
    var talents = result['talents'];
    text.innerHTML = talents.sort().join(', ') + '.';
    if (Object.values(talents).length == 0) 
      text.innerHTML = 'None.';

  text = document.querySelector('.abilities');
    var talents = result['abilities'];
    text.innerHTML = talents.sort().join(', ') + '.';
    if (Object.values(talents).length == 0) 
      text.innerHTML = 'None.';

  text = document.querySelector('.weapons'); 
  if ('weapons' in result) 
    text.textContent = result['weapons']
  else
    text.innerHTML = 'None.';

  text = document.querySelector('.equipment');
  if ('equipment' in result) 
    text.textContent = result['equipment']
  else
    text.innerHTML = 'None.';

  var defense = result.defense;
  
  for (var id in defense){
    text = document.getElementsByClassName(id)[0]
    text.textContent = defense[id]; 
  };
  
  update_url();
  warning();
  template();

}; 

function update_url(){
  var form = document.getElementById('type');
  var params = new URLSearchParams(new FormData(form));
  
  var url = window.location.pathname + '?' + params.toString();
  history.replaceState("", "", url);
};

function update_name() {
  name_adver = document.querySelector('input[placeholder="Name"]').value;
  var field = document.getElementById('name');
  field.innerText = (name_adver == "") ? 'Name' : name_adver;
  
  update_url();
  //template();
};

function loading(){
  searchParams = new URLSearchParams(window.location.search);

  for (const [key, value] of searchParams) {
    var input = document.querySelector('input[name="' + key + '"][value="' + value + '"]') ;
    if (input === null){
      // probably a text input
      var input = document.querySelector('input[name="' + key + '"]') ;
      input.value = value;
    } else 
      input.checked = true;
  };
};

function warning(){
  warnings = []

  // find all checked defense elements
  var defense_inputs = document.querySelectorAll('table input[name="defense"]');
  var nb_checked = 0;
  for (var i=0, n=defense_inputs.length, input; i < n; i++){
    input = defense_inputs[i];
    if (input.checked) 
      nb_checked++
  }

  if (nb_checked > 2 || (nb_checked > 1 && adversary_type == 'minion'))
    warnings.push('Too many defense options selected.');

  if (result['defense']['soak'] > 7)
    warnings.push('Soak should not be above 7.');


  if (result['defense']['melee_defense'] > 4 || result['defense']['ranged_defense'] > 4)
    warnings.push('A defense rating must not be above 4.');


  // Check thresholds
  //

  if (Object.values(result['skills']).length > 8)
    warnings.push('The maximum recommanded number of skills is 8; you may discard any unnescessary.');


  // Check talents


  // Affichage

  if (warnings.length > 0) {
    document.getElementById('warn').style.display = "initial";
    var list = document.querySelector('.warnings');
    list.innerHTML = "";
    for (element of warnings) {
      var li = document.createElement('li');
      li.textContent = element;
      list.appendChild(li);
    };
  } else document.getElementById('warn').style.display = "none";
  
};

function template(){
  //if (display_template){
  var content = ["{{" + adversary_type];
  
  content.push("name=" + name_adver);
  
  var caracs = result['caracteristics'];
  for (var id in caracs){
    content.push(id + "=" + caracs[id])
  };

  var level = result['power_level'];
  for (var id in level)
    content.push(id + "=" + level[id]);
  
  var skills = result['skills'];
  if (Object.values(skills).length > 0) {
    var skill_array = [];
    for (name in skills)
      skill_array.push(name + ' ' + skills[name]);
    content.push('skills=' + skill_array.sort().join(', ') + '.');
  };

  var talents = result['talents'];
  if (Object.values(talents).length > 0) 
    content.push('talents=' + talents.sort().join(', ') + '.');

  var talents = result['abilities'];
  if (Object.values(talents).length > 0) 
    content.push('abilities=' + talents.sort().join(', ') + '.');

  if ('weapons' in result) 
    content.push('weapons=' + result['weapons']);

  if ('equipment' in result) 
    content.push('equipment=' + result['equipment']);

  var defense = result.defense;
  for (var id in defense)
    content.push(id + '=' + defense[id]);

  // Affichage
  var area = document.querySelector('textarea');
  var templ = content.join('\n |') + "\n}}";
  area.value = templ;

  area.style.height = "";
  area.style.height = area.scrollHeight + "px";

  return templ
  //}
}

function toogle_template(){
  if (typeof display_template === 'undefined')
    display_template = false;
  else 
    display_template = !display_template;

  var area = document.querySelector('textarea')
  var copy_button =  document.getElementById('copy');
  if (display_template) {
    area.style.display = 'unset';
    area.style.height = area.scrollHeight + "px";
    area.focus();
    //area.select();
  copy_button.style.display = 'unset';
      
  } else {
    area.style.display = 'none';
  copy_button.style.display = 'none';
  }
  return area

}

function copy(){
  var area = document.querySelector('textarea')
  area.select();
  document.execCommand("copy");
  area.setSelectionRange(0, 0);
}
  
loading();
toogle_template();
update_name();
update();

