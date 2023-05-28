// [
//     "\"New research at Washington University School of Medicine in St. Louis shows that people who struggle with mood problems or addiction can safely quit smoking and that kicking the habit is associated with improved mental health.\"",
//     "\"In addition, she believes the serious health risks associated with smoking make it important for doctors to work with their patients to quit, regardless of other psychiatric problems.\"",
//     "\"About half of all smokers die from related to smoking, so we need to remember that as complicated as it can be to treat mental health issues, smoking cigarettes also causes very serious illnesses that can lead to death,\" she explained.",
//     "\"We really need to spread the word and encourage doctors and patients to tackle these problems,\" Cavazos-Rehg said. \"When a patient is ready to focus on other mental health issues, it may be an ideal time to address smoking cessation, too.\""
//   ]

// [
//     ""New research at Washington University School of Medicine in St. Louis shows that people who struggle with mood problems or addiction can safely quit smoking and that kicking the habit is associated with improved mental health."",
//     ""In addition, she believes the serious health risks associated with smoking make it important for doctors to work with their patients to quit, regardless of other psychiatric problems."",
//     ""About half of all smokers die from related to smoking, so we need to remember that as complicated as it can be to treat mental health issues, smoking cigarettes also causes very serious illnesses that can lead to death," she explained.",
//     ""We really need to spread the word and encourage doctors and patients to tackle these problems,\" Cavazos-Rehg said. \"When a patient is ready to focus on other mental health issues, it may be an ideal time to address smoking cessation, too.""
//   ]

const input = [
    "\"New research at Washington University School of Medicine in St. Louis shows that people who struggle with mood problems or addiction can safely quit smoking and that kicking the habit is associated with improved mental health.\"",
    "\"In addition, she believes the serious health risks associated with smoking make it important for doctors to work with their patients to quit, regardless of other psychiatric problems.\"",
    "\"About half of all smokers die from related to smoking, so we need to remember that as complicated as it can be to treat mental health issues, smoking cigarettes also causes very serious illnesses that can lead to death,\" she explained.",
    "\"We really need to spread the word and encourage doctors and patients to tackle these problems,\" Cavazos-Rehg said. \"When a patient is ready to focus on other mental health issues, it may be an ideal time to address smoking cessation, too.\""
  ];
  

  const escapedList = input.map((item, index) => `index ${index}: ${item.replace(/"/g, '\\"')}`);

  escapedList.forEach(item => console.log(item));