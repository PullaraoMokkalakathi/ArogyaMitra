export const workoutVideos: Record<string, string> = {
  "Bicep Curl": "https://www.youtube.com/embed/ckhfQgBfj6w",
  "Bench Press": "https://www.youtube.com/embed/sRuKSZLcmWM",
  "Cable Crossovers": "https://www.youtube.com/embed/y4RJDSOBEl8",
  "Hammer Curls": "https://www.youtube.com/embed/jdYGDzCuGE4",
  "Seated Cable Row": "https://www.youtube.com/embed/11kZYDXrdf4",
  "Lat Pulldown": "https://www.youtube.com/embed/TddgAFsS0m8",
  "Tricep Pushdown": "https://www.youtube.com/embed/XpeCPOHJTK8",
  "Lunges": "https://www.youtube.com/embed/D9D015V_PiA",
  "Calf Raises": "https://www.youtube.com/embed/di_lgImt2_M",
  "Plank": "https://www.youtube.com/embed/xe2MXatLTUw",
  "Reverse Pec Deck": "https://www.youtube.com/embed/XFnxc7gOIh8",
  "Shoulder Press": "https://www.youtube.com/embed/-Nw2nMEKvZc",
  "Russian Twists": "https://www.youtube.com/embed/-cPtvFdT8dc",
  "Lateral Raises": "https://www.youtube.com/embed/Kl3LEzQ5Zqs",
  "Chest Fly": "https://www.youtube.com/embed/NEXwXAJ3D2A",
  "Squats": "https://www.youtube.com/embed/ur1GLRQq8k0",
  "Pushups": "https://www.youtube.com/embed/_l3ySVKYVJ8",
};

export const getWorkoutVideo = (workoutName: string): string => {
  const normalizedName = workoutName.trim();
  return workoutVideos[normalizedName] || "https://www.youtube.com/embed/ur1GLRQq8k0";
};