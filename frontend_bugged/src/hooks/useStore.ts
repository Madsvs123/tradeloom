import  useSyncExternalStore } from "react";
import type { Store } from "../store/createStore";

export function useStore<T>(store: Store<T>): T;
export function useStore<T, S>(store: Store<T>, selector: (state: T) => S): S;
export function useStore<T, S>(store: Store<T>, selector?: (state: T) => S): T | S {
  return useSyncExternalStore(
    store.subscribe,
    () => (selector ? selector(store.getState()) : store.getState()),
    () => (selector ? selector(store.getState()) : store.getState()),
  );
}
