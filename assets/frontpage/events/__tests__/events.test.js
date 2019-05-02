import React from 'react';
import { mount, configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import SmallEvent from '../components/SmallEvent';

configure({ adapter: new Adapter() });

describe('<SmallEvent />', () => {
  const testUrl = 'thisIsUrl';
  const testDate = '2013-02-08';
  const wrapper = mount(<SmallEvent eventUrl={testUrl} startDate={testDate} title="event" />);

  it('renders a small event with a href to the the correct url', () => {
    expect(wrapper.find({ href: testUrl })).toBeDefined();
  });
});
