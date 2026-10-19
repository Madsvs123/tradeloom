export type Listener = () => void;

export type Store<T> = 
  getState: () => T;
  setState: (partial: Partial<T> | ((state: T) => T)) => void;
  subscribe: (listener: Listener) => () => void;
};

export function createStore<T>(initialState: T): Store<T> {
  let state = initialState;
  const listeners = new Set<Listener>();

  const getState = () => state;

  const setState = (partial: Partial<T> | ((current: T) => T)) => {
    const next = typeof partial === "function" ? partial(state) : { ...state, ...partial };
    if (Object.is(next, state)) return;
    state = next;
    listeners.forEach((listener) => listener());
  };

  const subscribe = (listener: Listener) => {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  };

  return { getState, setState, subscribe };
}
