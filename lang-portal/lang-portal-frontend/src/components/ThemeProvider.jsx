import { createContext, useContext, useEffect, useState } from "react";

// Create a theme context
const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  // Check for saved theme or use system default
  const getInitialTheme = () => {
    if (typeof window !== "undefined" && window.localStorage) {
      const storedTheme = window.localStorage.getItem("theme");
      if (storedTheme) {
        return storedTheme;
      }

      // Check for system preference
      const userMedia = window.matchMedia("(prefers-color-scheme: dark)");
      if (userMedia.matches) {
        return "dark";
      }
    }

    // Default to light theme
    return "light";
  };

  const [theme, setTheme] = useState(getInitialTheme);
  const [resolvedTheme, setResolvedTheme] = useState(getInitialTheme);

  const rawSetTheme = (theme) => {
    const root = window.document.documentElement;
    const isDark = theme === "dark";

    root.classList.remove(isDark ? "light" : "dark");
    root.classList.add(theme);

    localStorage.setItem("theme", theme);
  };

  // Update the theme
  const setThemeValue = (value) => {
    setTheme(value);
    if (value === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
      setResolvedTheme(systemTheme);
      rawSetTheme(systemTheme);
    } else {
      setResolvedTheme(value);
      rawSetTheme(value);
    }
  };

  // Initialize theme
  useEffect(() => {
    // Set up system theme listener
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    
    const handleChange = () => {
      if (theme === "system") {
        const newTheme = mediaQuery.matches ? "dark" : "light";
        setResolvedTheme(newTheme);
        rawSetTheme(newTheme);
      }
    };
    
    mediaQuery.addEventListener("change", handleChange);
    
    // Apply initial theme
    if (theme === "system") {
      const systemTheme = mediaQuery.matches ? "dark" : "light";
      setResolvedTheme(systemTheme);
      rawSetTheme(systemTheme);
    } else {
      rawSetTheme(theme);
    }
    
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [theme]);

  return (
    <ThemeContext.Provider 
      value={{ 
        theme, 
        setTheme: setThemeValue, 
        resolvedTheme 
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};